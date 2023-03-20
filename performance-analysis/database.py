import sqlite3
from typing import Iterable, Union


_INTEGER = 'INTEGER'
_PRIMARY_KEY = 'PRIMARY KEY'
_REAL = 'REAL'
_TEXT = 'TEXT'

OptionalInt = Union[int, None]
OptionalStringList = Union[list[str], None]

IdMap = dict[str, OptionalInt]


class _Context(object):
    _connection: sqlite3.Connection
    _cursor: sqlite3.Cursor

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
        self._cursor = self._connection.cursor()

    def execute(self, statement: str) -> None:
        self._execute(statement)

    def insert(self, table_name: str, fields: list[str], values: list) -> None:
        statement = f'''INSERT INTO {table_name} ({", ".join(fields)})
                        VALUES ({", ".join(["?"] * len(fields))})'''

        self._cursor.executemany(statement, values)
        self._connection.commit()

    def query(self, statement: str) -> list[tuple]:
        return list([tuple(row) for row in self._execute(statement)])

    def select(self, table_name: str, fields: list[str], where: list[str] = []) -> list[tuple]:
        parts = [
            'SELECT', ', '.join(fields),
            'FROM', table_name,
        ]

        if len(where) > 0:
            parts.append('WHERE')
            parts.append(' AND '.join(where))

        return self.query(' '.join(parts))

    def last_insert_id(self) -> int:
        for row in self._cursor.execute('SELECT last_insert_rowid()'):
            return row[0]

    def _execute(self, statement: str) -> sqlite3.Cursor:
        return self._cursor.execute(statement)


class _Column(object):
    PRIMARY_KEY: int = 1 << 0
    AUTO_INCREMENT: int = 1 << 1
    INDEXED: int = 1 << 2
    UNIQUE: int = 1 << 3

    name: str
    type_name: str
    _flags: int

    def __init__(self, name: str, type_name: str) -> None:
        self.name = name
        self.type_name = type_name
        self._flags = 0

    def auto_increment(self) -> '_Column':
        self._flags |= _Column.AUTO_INCREMENT
        return self

    def indexed(self, unique: bool) -> '_Column':
        self._flags |= _Column.INDEXED
        if unique: self._flags |= _Column.UNIQUE
        return self

    def primary_key(self) -> '_Column':
        self._flags |= _Column.PRIMARY_KEY
        return self

    def is_auto_increment(self) -> bool:
        return (self._flags & _Column.AUTO_INCREMENT) != 0

    def is_indexed(self) -> bool:
        return (self._flags & _Column.INDEXED) != 0

    def is_primary_key(self) -> bool:
        return (self._flags & _Column.PRIMARY_KEY) != 0

    def is_unique(self) -> bool:
        return (self._flags & _Column.UNIQUE) != 0


class _Table(object):
    name: str
    _columns: list[_Column]

    def __init__(self, name: str, *columns: Iterable[_Column]) -> None:
        self.name = name
        self._columns = list(columns)

    def drop(self, context: _Context) -> None:
        context.execute(f'DROP TABLE IF EXISTS {self.name}')

    def create(self, context: _Context) -> None:
        self._create_table(context)
        self._create_indices(context)

    def insert(self, context: _Context, **kwargs) -> int:
        fields = list(kwargs.keys())
        values = list(kwargs.values())

        context.insert(self.name, fields, [values])
        row_id = context.last_insert_id()

        print(f'inserted row {row_id} into {self.name}: ({", ".join([str(v) for v in values])})')

        return row_id

    def insert_many(self, context: _Context, fields: OptionalStringList, values: list) -> None:
        fields = fields or [column.name for column in self._columns]
        context.insert(self.name, fields, values)

    def _create_table(self, context: _Context) -> None:
        fields = []
        primary_keys = [column for column in self._columns if column.is_primary_key()]

        for column in self._columns:
            field = f'{column.name} {column.type_name}'

            if len(primary_keys) == 1 and primary_keys[0] == column:
                field = f'{field} {_PRIMARY_KEY}'

            if column.is_auto_increment():
                field = f'{field} AUTOINCREMENT'

            fields.append(field)

        if len(primary_keys) > 1:
            primary_keys = ', '.join(column.name for column in primary_keys)
            fields.append(f'{_PRIMARY_KEY}({primary_keys})')

        context.execute(f'CREATE TABLE {self.name}({", ".join(fields)})')

    def _create_indices(self, context: _Context) -> None:
        for column in self._columns:
            if not column.is_indexed(): continue

            context.execute(f'''
                CREATE{" UNIQUE" if column.is_unique() else ""} INDEX
                {self.name}_{column.name}_idx
                ON {self.name}({column.name})''')


class _NameTable(_Table):
    _id_field: str
    _name_field: str

    def __init__(self, name: str, id_field: str, name_field: str, *columns: Iterable[_Column]) -> None:
        super().__init__(name, *columns)

        self._id_field = id_field
        self._name_field = name_field

    def get_ids(self, context: _Context, names: list[str], create_missing: bool, **kwargs) -> IdMap:
        conditions = [f'{k} = {v}' for k, v in kwargs.items()]
        ids = self._map_names_to_ids(context, names, conditions)

        if create_missing:
            missing_names = [name for name in names if ids[name] is None]

            if len(missing_names) > 0:
                ids.update(self._create_missing_names(context, missing_names, kwargs))

        return ids

    def _map_names_to_ids(self, context: _Context, names: list[str], conditions: list[str]) -> IdMap:
        ids: IdMap = {name: None for name in names}
        name_list = ', '.join([f'"{name}"' for name in names])

        conditions.append(f'{self._name_field} IN ({name_list})')

        for row in context.select(self.name, [self._id_field, self._name_field], conditions):
            ids[row[1]] = row[0]

        return ids

    def _create_missing_names(self, context: _Context, names: list[str], fields: dict) -> dict[str, int]:
        columns = [self._name_field] + list(fields.keys())
        ids: dict[str, int] = {}

        for name in names:
            context.insert(self.name, columns, [[name] + list(fields.values())])
            ids[name] = context.last_insert_id()

        return ids


class Database(object):
    _context: _Context
    _tables: list[_Table]

    def __init__(self, path: str) -> None:
        if path is None: raise ValueError('no database path specified')

        self._context = _Context(sqlite3.connect(path))
        self._tables = [
            _NameTable(
                'metrics', 'metric_id', 'metric_name',
                _Column('metric_id', _INTEGER).primary_key().auto_increment(),
                _Column('sdk_id', _INTEGER).indexed(False),
                _Column('module_id', _INTEGER).indexed(False),
                _Column('metric_name', _TEXT).indexed(True)
            ),
            _NameTable(
                'modules', 'module_id', 'module_name',
                _Column('module_id', _INTEGER).primary_key().auto_increment(),
                _Column('sdk_id', _INTEGER).indexed(False),
                _Column('module_name', _TEXT).indexed(False)
            ),
            _Table(
                'reports',
                _Column('report_id', _INTEGER).primary_key().auto_increment(),
                _Column('report_ts', _INTEGER).indexed(True)
            ),
            _Table(
                'samples',
                _Column('report_id', _INTEGER).primary_key(),
                _Column('metric_id', _INTEGER).primary_key(),
                _Column('sample_count', _INTEGER),
                _Column('sample_sd', _REAL),
                _Column('sample_min', _REAL),
                _Column('sample_max', _REAL),
                _Column('sample_mean', _REAL)
            ),
            _NameTable(
                'sdks', 'sdk_id', 'sdk_name',
                _Column('sdk_id', _INTEGER).primary_key().auto_increment(),
                _Column('sdk_name', _TEXT).indexed(True)
            ),
        ]

    def drop_all_tables(self) -> None:
        for table in self._tables:
            table.drop(self._context)

    def create_all_tables(self) -> None:
        for table in self._tables:
            table.create(self._context)

    def create_report(self, timestamp: int) -> int:
        return self._find_table('reports').insert(self._context, report_ts=timestamp)

    def get_metric_ids(self, names: list[str], create_missing: bool = True) -> IdMap:
        metric_parts = [(parts[0], parts[1], '.'.join(parts[2:])) for parts in [name.split('.') for name in names]]
        ids: IdMap = {name: None for name in names}

        sdks: _NameTable = self._find_table('sdks')
        modules: _NameTable = self._find_table('modules')
        metrics: _NameTable = self._find_table('metrics')

        sdk_names = list(set([parts[0] for parts in metric_parts]))
        sdk_ids = sdks.get_ids(self._context, sdk_names, create_missing)

        for sdk_name in sdk_names:
            if sdk_ids[sdk_name] is None: continue

            sdk_id = sdk_ids[sdk_name]
            sdk_metrics = [parts for parts in metric_parts if parts[0] == sdk_name]
            module_names = list(set([parts[1] for parts in sdk_metrics]))
            module_ids = modules.get_ids(self._context, module_names, create_missing, sdk_id=sdk_id)

            for module_name in module_names:
                if module_ids[module_name] is None: continue

                module_id = module_ids[module_name]
                module_metrics = [parts for parts in sdk_metrics if parts[1] == module_name]
                metric_names = list(set([parts[2] for parts in module_metrics]))
                metric_ids = metrics.get_ids(self._context, metric_names, create_missing, sdk_id=sdk_id, module_id=module_id)

                for metric_name in metric_names:
                    ids[f'{sdk_name}.{module_name}.{metric_name}'] = metric_ids[metric_name]

        return ids

    def insert_samples(self, samples: list) -> None:
        self._find_table('samples').insert_many(self._context, None, samples)

    def get_history(self, metric_ids: list[int]) -> list[tuple[int, float]]:
        recent_report_ids: list[int] = []
        statement = 'SELECT report_id FROM reports ORDER BY report_ts DESC LIMIT 20'

        for row in self._context.query(statement):
            recent_report_ids.append(row[0])

        return self._context.select('samples', ['metric_id', 'sample_mean'], where=[
            f'report_id IN ({", ".join([str(x) for x in recent_report_ids])})',
            f'metric_id IN ({", ".join([str(x) for x in metric_ids])})',
        ])

    def _find_table(self, table_name: str) -> _Table:
        for table in self._tables:
            if table.name == table_name:
                return table
