import os
import sys


def print_help():
    print(f'{os.path.basename(sys.argv[0])} command_name [report_path] [options]')
    print('')
    print('Available commands:')
    print('    compare             Generate a comparison between the report and the')
    print('                        historical data contained in the specified database.')
    print('    help                Display this message.')
    print('    import              Add the new report data to the specified database.')
    print('    initialize          Initializes a new database and creates the necessary')
    print('                        tables and keys.')
    print('')
    print('Available options:')
    print('    -d, --database      Path to the sqlite3 database containing the historical')
    print('                        performance data.')
