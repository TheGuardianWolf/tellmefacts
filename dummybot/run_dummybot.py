#!/usr/bin/env python3

"""
This is the launcher for the dummybot server.

    usage: run_dummybot.py [-h] [--config-dir CONFIG_DIR]

    Launches the dummybot server.

    optional arguments:
    -h, --help            show this help message and exit
    --config-dir CONFIG_DIR
                            changes the config directory
"""

from dummybot import Server
from argparse import ArgumentParser


def main():
    parser = ArgumentParser(description='Launches the dummybot server.')
    parser.add_argument('--config-dir', dest='config_dir', action='store',
                        help='changes the config directory')
    args = parser.parse_args()
    server_args = {}

    if args.config_dir is not None:
        server_args['config_path'] = args.config_dir

    s = Server(**server_args)
    s.start()


if __name__ == '__main__':
    main()
