#!/usr/bin/env python3
from client import MultibotClient
from argparse import ArgumentParser
from sys import exit
import pytest
import logging


def main():
    parser = ArgumentParser(description='Launches the slackbot client.')
    parser.add_argument(
        '--with-tests',
        dest='with_tests',
        action='store_true',
        help='run tests before starting client (skipping optional)')
    parser.add_argument(
        '--only-tests',
        dest='with_tests_all',
        action='store_true',
        help='run all tests including optional, don\'t start client')
    parser.add_argument(
        '--config-dir',
        dest='config_dir',
        action='store',
        help='changes the config directory')
    parser.add_argument(
        '--api-hostname',
        dest='api_hostname',
        action='store',
        help='sets a hostname other than slack.com')
    parser.add_argument(
        '--terminal',
        dest='terminal',
        action='store_true',
        help='set bot to run in terminal mode')
    parser.add_argument(
        '--verbose',
        dest='verbose',
        action='store_true',
        help='display all logging information on terminal')
    args = parser.parse_args()
    client_args = {}

    if args.with_tests or args.only_tests:
        pytest_args = []
        failure_message = 'ERROR: Tests failed, aborting start.'
        if args.only_tests:
            pytest_args.append('--dummybot')
            failure_message = 'ERROR: Tests failed'
        result = pytest.main(pytest_args)
        try:
            assert result == 0
        except AssertionError:
            exit(failure_message)

    if args.terminal:
        client_args['input_adapter'] = 'chatterbot.input.TerminalAdapter'
        client_args['output_adapter'] = 'chatterbot.output.TerminalAdapter'

    if args.config_dir is not None:
        client_args['config_path'] = args.config_dir

    if args.api_hostname is not None:
        client_args['api_hostname'] = args.api_hostname

    if args.verbose:
        logging.basicConfig(level=logging.INFO)

    if not args.only_tests:
        c = MultibotClient(**client_args)
        c.start()


if __name__ == '__main__':
    main()
