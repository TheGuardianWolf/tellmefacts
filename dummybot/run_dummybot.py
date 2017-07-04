#!/usr/bin/env python3
from dummybot import Server
from argparse import ArgumentParser
import pytest


def main():
    parser = ArgumentParser(description='Launches the dummybot server.')
    parser.add_argument('--with-tests', dest='with_tests', action='store_true',
                        help='run tests before starting server')
    parser.add_argument('--config-dir', dest='config_dir', action='store',
                        help='changes the config directory')
    args = parser.parse_args()

    if args.with_tests is True:
        pytest.main(['-s'])

    s = Server(config_path=args.config_dir)
    s.start()


if __name__ == '__main__':
    main()
