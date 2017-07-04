#!/usr/bin/env python3
from client import MultibotClient
from argparse import ArgumentParser
import pytest


def main():
    parser = ArgumentParser(description='Launches the slackbot client.')
    parser.add_argument('--with-tests', dest='with_tests', action='store_true',
                        help='run tests before starting client')
    parser.add_argument('--config-dir', dest='config_dir', action='store',
                        help='changes the config directory')
    parser.add_argument('--data-dir', dest='data_dir', action='store',
                        help='changes the data directory')
    args = parser.parse_args()

    if args.with_tests is True:
        pytest.main()

    c = MultibotClient(config_path=args.config_dir, data_path=args.data_dir)
    c.start()


if __name__ == '__main__':
    main()
