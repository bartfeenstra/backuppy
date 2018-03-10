"""Provide CLI components."""
from __future__ import absolute_import
import argparse

from backuppy.config import from_json, from_yaml
from backuppy.task import backup


def main(args):
    """Provide the CLI entry point."""
    parser = argparse.ArgumentParser(description='Backs up your data.')
    parser.add_argument('-c', '--configuration', action='store', required=True,
                        help='The path to the back-up configuration file.')
    cli_args = vars(parser.parse_args(args))
    configuration_file_path = cli_args['configuration']
    with open(configuration_file_path) as f:
        if f.name.endswith('.json'):
            configuration = from_json(f)
        elif f.name.endswith('.yml') or f.name.endswith('.yaml'):
            configuration = from_yaml(f)
        else:
            raise ValueError('Configuration files must have *.json, *.yml, or *.yaml extensions.')

        backup(configuration)
