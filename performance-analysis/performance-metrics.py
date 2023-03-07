#!/usr/bin/env python3

import sys

from arguments import parse_args
from compare import compare_report
from database import Database
from help import print_help
from ingest import ingest_report


if __name__ == '__main__':
    command_name, database_path, report_path = parse_args(sys.argv[1:])

    if command_name is None or command_name == 'help':
        print_help()
        sys.exit(0)

    db = Database(database_path)

    match command_name:
        case 'compare':
            compare_report(db, report_path)
        case 'ingest':
            ingest_report(db, report_path)
        case 'initialize':
            db.drop_all_tables()
            db.create_all_tables()
        case _:
            raise Exception(f'unknown command: {command_name}')
