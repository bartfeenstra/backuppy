"""Provide CLI components."""
import argparse

from backuppy.config import from_json
from backuppy.runner import Runner


def main(args):
    """Provide the CLI entry point."""
    parser = argparse.ArgumentParser(description='Backs up your data.')
    parser.add_argument('-c', '--configuration', action='store', required=True,
                        help='The path to the back-up configuration file.')
    cli_args = vars(parser.parse_args(args))
    configuration_file_path = cli_args['configuration']
    with open(configuration_file_path) as f:
        configuration = from_json(f)
        runner = Runner(configuration)
        runner.backup()
