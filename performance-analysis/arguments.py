from typing import Iterable, Union


OptionalString = Union[str, None]


def parse_args(args: list[str]) -> tuple[OptionalString, OptionalString, OptionalString]:
    command_name: OptionalString = None
    database_path: OptionalString = None
    report_path: OptionalString = None
    index, count = 0, len(args)

    while index < count:
        arg = args[index]

        if arg.startswith('-'):
            if arg == '-d' or arg == '--database':
                index += 2

                if index > count:
                    raise Exception(f'expected database path after {arg}')

                database_path = args[index - 1]
            else:
                raise Exception(f'unknown parameter: {arg}')
        elif command_name is None:
            command_name = arg
            index += 1
        elif report_path is None:
            report_path = arg
            index += 1
        else:
            raise Exception(f'unexpected argument: {arg}')

    return command_name, database_path, report_path
