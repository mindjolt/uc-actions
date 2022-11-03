#!/usr/bin/env python3

import sys
import os
import re


RE_NAMES = re.compile(r'(\w+)')


def get_parameters():
    project_path, remove_symbols, symbols, platforms = None, None, None, None
    environment = os.environ
    args = sys.argv[1:]

    while len(args) > 0:
        arg, args = args[0], args[1:]

        if arg == '-r' or arg == '--remove-symbols':
            if remove_symbols is not None:
                raise Exception(f'Unexpected "{arg}" encountered')

            remove_symbols = True
        elif arg == '-s' or arg == '--symbols':
            if symbols is not None:
                raise Exception(f'Unexpected "{arg}" encountered')

            if len(args) == 0:
                raise Exception(f'Expected list of symbols after "{arg}"')

            symbols, args = args[0], args[1:]
        elif arg == '-p' or arg == '--platforms':
            if platforms is not None:
                raise Exception(f'Unexpected "{arg}" encountered')

            if len(args) == 0:
                raise Exception(f'Expected list of platforms after "{arg}"')

            platforms, args = args[0], args[1:]
        elif arg.startswith('-'):
            raise Exception(f'Unknown parameter "{arg}" encountered')
        else:
            if project_path is not None:
                raise Exception(f'More than one project path specified: "{arg}"')

            project_path = arg

    if project_path is None:
        if 'INPUT_PROJECT_PATH' not in environment:
            raise Exception('No project path was specified')

        project_path = environment['INPUT_PROJECT_PATH']

    if remove_symbols is None:
        remove_symbols = (('INPUT_REMOVE_SYMBOLS' in environment) and
                          (environment['INPUT_REMOVE_SYMBOLS'] in ['true', 'True']))

    if symbols is None:
        if 'INPUT_SYMBOLS' not in environment:
            raise Exception('No symbols were specified')

        symbols = environment['INPUT_SYMBOLS']

    symbols = [s.strip() for s in RE_NAMES.findall(symbols)]

    if len(symbols) == 0:
        raise Exception('No symbols were provided')

    if (platforms is None) and ('INPUT_PLATFORMS' in environment):
        if environment['INPUT_PLATFORMS'].strip() != '':
            platforms = environment['INPUT_PLATFORMS']

    if platforms is not None:
        platforms = [p.strip() for p in RE_NAMES.findall(platforms)]

        if len(platforms) == 0:
            raise Exception('Platform list is invalid')

    return project_path, remove_symbols, symbols, platforms


if __name__ == '__main__':
    project_path, remove_symbols, symbols, platforms = get_parameters()
    input_path = os.path.join(project_path, 'ProjectSettings/ProjectSettings.asset')
    output, state = [], 0

    # None of the YAML libraries handled this properly, so just edit the file
    # as a stream since we know the format and layout we care about.
    with open(input_path, 'rt') as in_file:
        for line in in_file:
            if (((state == 0) and (line == '  scriptingDefineSymbols:\n')) or
                ((state == 1) and (not line.startswith('    ')))):
                    state += 1

            if (state == 1) and line.startswith('    '):
                key, value = line.split(':')
                platform = key.strip()
                define_symbols = list(RE_NAMES.findall(value.strip()))

                if platforms is None or platform in platforms:
                    for symbol in symbols:
                        if remove_symbols and symbol in define_symbols:
                            print(f'Removing symbol "{symbol}" from platform "{platform}"')
                            define_symbols.remove(symbol)
                        elif not remove_symbols and symbol not in define_symbols:
                            print(f'Adding symbol "{symbol}" to platform "{platform}"')
                            define_symbols.append(symbol)

                value = ';'.join(define_symbols)
                line = f'{key}: {value}\n'

            output.append(line)

    with open(input_path, 'wt') as f:
        for line in output:
            f.write(line)
