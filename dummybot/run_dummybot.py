#!/usr/bin/env python3
from dummybot import Server
from argparse import ArgumentParser
from sys import exit
import pytest


def main():
    parser = ArgumentParser(description='Launches the dummybot server.')
    parser.add_argument('--with-tests', dest='with_tests', action='store_true',
                        help='run tests before starting server')
    parser.add_argument('--config-dir', dest='config_dir', action='store',
                        help='changes the config directory')
    args = parser.parse_args()
    server_args = {}

    if args.with_tests is True:
        result = pytest.main(['-s'])
        try:
            assert result == 0
        except AssertionError:
            exit('ERROR: Tests failed, aborting start.')

    if args.config_dir is not None:
        server_args['config_path'] = args.config_dir

    s = Server(**server_args)
    s.start()


if __name__ == '__main__':
    main()
