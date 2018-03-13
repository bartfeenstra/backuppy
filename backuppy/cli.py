"""Provide CLI components."""
from __future__ import absolute_import

import argparse

from backuppy.config import from_json, from_yaml
from backuppy.task import backup


class ConfigurationAction(argparse.Action):
    """Provide a Semantic Version action."""

    def __init__(self, *args, **kwargs):
        """Initialize a new instance."""
        argparse.Action.__init__(self, *args, required=True, help='The path to the back-up configuration file.',
                                 **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Invoke the action."""
        configuration_file_path = values
        with open(configuration_file_path) as f:
            if f.name.endswith('.json'):
                configuration = from_json(f)
            elif f.name.endswith('.yml') or f.name.endswith('.yaml'):
                configuration = from_yaml(f)
            else:
                raise ValueError('Configuration files must have *.json, *.yml, or *.yaml extensions.')

            setattr(namespace, self.dest, configuration)


def main(args):
    """Provide the CLI entry point."""
    parser = argparse.ArgumentParser(description='Backuppy backs up and restores your data using rsync.')
    subparsers = parser.add_subparsers()
    backup_parser = subparsers.add_parser('backup', help='Starts a back-up.')
    backup_parser.add_argument('-c', '--configuration', action=ConfigurationAction)
    backup_parser.set_defaults(func=lambda subparser_cli_args: backup(subparser_cli_args['configuration']))
    cli_args = parser.parse_args(args)
    if 'func' in cli_args:
        cli_args.func(vars(cli_args))
    else:
        parser.print_help()
