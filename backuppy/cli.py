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
        verbose = None
        if namespace.quiet:
            verbose = False
        if namespace.verbose:
            verbose = True
        configuration_file_path = values
        with open(configuration_file_path) as f:
            if f.name.endswith('.json'):
                configuration_factory = from_json
            elif f.name.endswith('.yml') or f.name.endswith('.yaml'):
                configuration_factory = from_yaml
            else:
                raise ValueError('Configuration files must have *.json, *.yml, or *.yaml extensions.')
            configuration = configuration_factory(f, verbose=verbose)

            setattr(namespace, self.dest, configuration)


def add_configuration_to_args(parser):
    """Add configuration options to a parser.

    :param parser: argparse.ArgumentParser
    :return: argparse.ArgumentParser
    """
    parser_verbosity = parser.add_mutually_exclusive_group()
    parser_verbosity.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                                  help='Generate verbose output. This overrides the value in the configuration file.')
    parser_verbosity.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                                  help='Do not generate verbose output. This overrides the value in the configuration file.')
    parser.add_argument('-c', '--configuration', action=ConfigurationAction)
    parser.set_defaults(func=lambda subparser_cli_args: backup(subparser_cli_args['configuration']))
    return parser


def main(args):
    """Provide the CLI entry point."""
    parser = argparse.ArgumentParser(description='Backuppy backs up and restores your data using rsync.',
                                     add_help=False)
    subparsers = parser.add_subparsers()
    backup_parser = subparsers.add_parser('backup', help='Starts a back-up.')
    add_configuration_to_args(backup_parser)

    cli_args = parser.parse_args(args)
    if 'func' in cli_args:
        cli_args.func(vars(cli_args))
    else:
        parser.print_help()
