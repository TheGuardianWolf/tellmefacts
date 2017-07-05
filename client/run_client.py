#!/usr/bin/env python3
from client import MultibotClient
from argparse import ArgumentParser
from sys import exit
import pytest


def main():
    parser = ArgumentParser(description='Launches the slackbot client.')
    parser.add_argument('--with-tests', dest='with_tests', action='store_true',
                        help='run tests before starting client')
    parser.add_argument('--config-dir', dest='config_dir', action='store',
                        help='changes the config directory')
    parser.add_argument('--terminal', dest='terminal', action='store_true',
                        help='set bot to run on terminal mode')
    args = parser.parse_args()
    client_args = {}

    if args.with_tests:
        result = pytest.main([])
        try:
            assert result == 0
        except AssertionError:
            exit('ERROR: Tests failed, aborting start.')

    if args.terminal:
        client_args['input_adapter'] = 'chatterbot.input.TerminalAdapter'
        client_args['output_adapter'] = 'chatterbot.output.TerminalAdapter'

    if args.config_dir is not None:
        client_args['config_path'] = args.config_dir

    c = MultibotClient(**client_args)
    c.start()


if __name__ == '__main__':
    main()
