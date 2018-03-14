"""Provide CLI components."""
from __future__ import absolute_import

import argparse

from backuppy import task
from backuppy.config import from_json, from_yaml


class ConfigurationAction(argparse.Action):
    """Provide a Semantic Version action."""

    def __init__(self, *args, **kwargs):
        """Initialize a new instance."""
        kwargs.setdefault('required', True)
        kwargs.setdefault('help', 'The path to the back-up configuration file.')
        argparse.Action.__init__(self, *args, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        """Invoke the action."""
        configuration_file_path = values

        verbose = None
        if namespace.quiet:
            verbose = False
        if namespace.verbose:
            verbose = True
        with open(configuration_file_path) as f:
            if f.name.endswith('.json'):
                configuration_factory = from_json
            elif any(map(f.name.endswith, ['.yml', 'yaml'])):
                configuration_factory = from_yaml
            else:
                raise ValueError('Configuration files must have *.json, *.yml, or *.yaml extensions.')
            configuration = configuration_factory(f, verbose=verbose)

            setattr(namespace, self.dest, configuration)


def add_configuration_to_parser(parser):
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
    return parser


def add_backup_command_to_parser(parser):
    """Add the back-up command to a parser.

    :param parser: argparse.ArgumentParser
    :return: argparse.ArgumentParser
    """
    backup_parser = parser.add_parser('backup', help='Starts a back-up.')
    backup_parser.set_defaults(func=lambda parsed_args: task.backup(parsed_args.configuration))
    add_configuration_to_parser(backup_parser)
    return parser


def add_commands_to_parser(parser):
    """Add Backuppy commands to a parser.

    :param parser: argparse.ArgumentParser
    :return: argparse.ArgumentParser
    """
    subparsers = parser.add_subparsers()
    add_backup_command_to_parser(subparsers)
    return subparsers


def main(args):
    """Provide the CLI entry point."""
    parser = argparse.ArgumentParser(description='Backuppy backs up and restores your data using rsync.')
    add_commands_to_parser(parser)

    parsed_args = parser.parse_args(args)
    if 'func' in parsed_args:
        try:
            parsed_args.func(parsed_args)
        except KeyboardInterrupt:
            # Quit gracefully.
            print('Quitting...')
        except BaseException:
            configuration = parsed_args.configuration
            configuration.logger.exception('A fatal error occurred.')
            configuration.notifier.alert('A fatal error occurred. Details have been logged as per your configuration.')
    else:
        parser.print_help()
