"""Provide CLI components."""
from __future__ import absolute_import

import argparse
import json
import re
from logging import Handler, WARNING

import yaml

from backuppy import task
from backuppy.config import from_json, from_yaml
from backuppy.notifier import StdioNotifier

FORMAT_JSON_EXTENSIONS = ('json',)
FORMAT_YAML_EXTENSIONS = ('yml', 'yaml')


def _input(prompt=None):
    """Wrap input() and raw_input() on Python 3 and 2 respectively.

    :param prompt: Optional[str]
    :return: str
    """
    try:
        return raw_input(prompt)
    except NameError:
        return input(prompt)


class StdioNotifierLoggingHandler(Handler):
    """Log warnings and more severe records to stdio."""

    def __init__(self):
        """Initialize a new instance."""
        Handler.__init__(self, WARNING)
        self._notifier = StdioNotifier()

    def emit(self, record):
        """Log a record.

        :param record: logging.LogRecord
        """
        self._notifier.alert(self.format(record))


class ConfigurationAction(argparse.Action):
    """Provide a Semantic Version action."""

    def __init__(self, *args, **kwargs):
        """Initialize a new instance."""
        kwargs.setdefault('required', True)
        kwargs.setdefault(
            'help', 'The path to the back-up configuration file.')
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
            if any(map(f.name.endswith, FORMAT_JSON_EXTENSIONS)):
                configuration_factory = from_json
            elif any(map(f.name.endswith, FORMAT_YAML_EXTENSIONS)):
                configuration_factory = from_yaml
            else:
                raise ValueError(
                    'Configuration files must have *.json, *.yml, or *.yaml extensions.')
            configuration = configuration_factory(f, verbose=verbose)

            # Ensure at least some form of error logging is enabled.
            logger = configuration.logger
            logger.disabled = False
            if logger.getEffectiveLevel() > WARNING:
                logger.setLevel(WARNING)
            if not logger.handlers:
                configuration.notifier.inform(
                    'The configuration does not specify any logging handlers for "backuppy", so all log records about problems will be displayed here.')
                logger.addHandler(StdioNotifierLoggingHandler())

            setattr(namespace, self.dest, configuration)


def add_configuration_to_parser(parser):
    """Add configuration options to a parser.

    :param parser: argparse.ArgumentParser
    :return: argparse.ArgumentParser
    """
    parser.add_argument('-c', '--configuration', action=ConfigurationAction)
    add_verbose_to_args(parser)
    return parser


def add_verbose_to_args(parser):
    """Add verbosity options to a parser.

    :param parser: argparse.ArgumentParser
    :return: argparse.ArgumentParser
    """
    parser_verbosity = parser.add_mutually_exclusive_group()
    parser_verbosity.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                                  help='Generate verbose output. This overrides the value in the configuration file.')
    parser_verbosity.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                                  help='Do not generate verbose output. This overrides the value in the configuration file.')
    return parser


def add_backup_command_to_parser(parser):
    """Add the back-up command to a parser.

    :param parser: argparse.ArgumentParser
    :return: argparse.ArgumentParser
    """
    backup_parser = parser.add_parser('backup', help='Starts a back-up.')
    backup_parser.set_defaults(
        func=lambda parsed_args: task.backup(parsed_args.configuration))
    add_configuration_to_parser(backup_parser)
    return parser


def add_init_command_to_parser(parser):
    """Add the configuration initialization command to a parser.

    :param parser: argparse.ArgumentParser
    :return: argparse.ArgumentParser
    """
    init_parser = parser.add_parser(
        'init', help='Initializes a new back-up configuration.')
    init_parser.set_defaults(func=lambda parsed_args: init())
    return parser


def add_commands_to_parser(parser):
    """Add Backuppy commands to a parser.

    :param parser: argparse.ArgumentParser
    :return: argparse.ArgumentParser
    """
    subparsers = parser.add_subparsers()
    add_backup_command_to_parser(subparsers)
    add_init_command_to_parser(subparsers)
    return parser


def ask_confirm(value_label, question=None, default=None):
    """Ask for a confirmation.

    :param value_label: str
    :param question: Optional[None]
    :param default: Optional[bool]
    :return: bool
    """
    if default is None:
        options_label = '(y/n)'
    elif default:
        options_label = '[Y/n]'
    else:
        options_label = '[y/N]'
    confirmation = None
    while confirmation is None:
        if question is not None:
            print(question)
        confirmation_input = _input('%s %s: ' % (
            value_label, options_label)).lower()
        if 'y' == confirmation_input:
            confirmation = True
        elif 'n' == confirmation_input:
            confirmation = False
        elif '' == confirmation_input and default is not None:
            confirmation = default
        else:
            print('That is not a valid confirmation. Enter "y" or "n".')
    return confirmation


def ask_any(value_label, question=None, required=True, validator=None):
    """Ask for any value.

    :param value_label: str
    :param question: Optional[None]
    :param required: Optional[bool]
    :param validator: Optional[Callable]
    :return: bool
    """
    string = None
    while string is None:
        if question is not None:
            print(question)
        string_input = _input(value_label + ': ')
        if validator:
            string = validator(string_input)
        elif not required or len(string_input):
            string = string_input
        else:
            print('You are required to enter a value.')
    return string


def ask_option(value_label, options, question=None):
    """Ask for a single item to be chosen from a collection.

    :param value_label: str
    :param options: Iterable[Tuple[Any, str]]
    :param question: Optional[None]
    :return: bool
    """
    if len(options) == 1:
        return options[0][0]

    option = None
    options_labels = []
    indexed_options = [(index, value, label)
                       for index, (value, label) in enumerate(options)]
    for index, _, option_label in indexed_options:
        options_labels.append('%d) %s' % (index, option_label))
    options_label = '0-%d' % (len(options) - 1)
    while option is None:
        if question is not None:
            print(question)
            print('\n'.join(options_labels))
        option_input = _input('%s (%s): ' % (value_label, options_label))
        try:
            if re.search('^\d+$', option_input) is None:
                raise IndexError()
            index_input = int(option_input)
            option = indexed_options[index_input][1]
        except IndexError:
            print('That is not a valid option. Enter %s.' % options_label)
    return option


def init():
    """Run a wizard to initialize a new back-up configuration file."""
    print('Welcome to Backuppy!\n')
    print(
        'You will now create a new back-up configuration file by answering a few questions as they appear on screen.\n')
    name = ask_any('Name',
                   question='What is the name of this back-up? Leave blank to use the configuration file name automatically.',
                   required=False)
    verbose = ask_confirm(
        'Verbose output', question='Do you want back-ups to output verbose notifications?', default=True)
    source_path = ask_any(
        'Source path', question='What is the path to the directory you want to back up?')
    target_path = ask_any(
        'Target path', question='What is the path to the directory you want to back up your data to?')
    format_options = [
        ('yaml', 'YAML (https://en.wikipedia.org/wiki/YAML)'),
        ('json', 'JSON (https://en.wikipedia.org/wiki/JSON)'),
    ]
    # @todo Default to YAML, because it's more human-readable and we can include code comments.
    format = ask_option('File format', format_options,
                        question='How should the configuration file be formatted?')

    configuration_data = {
        'verbose': verbose,
        'notifications': [
            {
                'type': 'stdio',
            },
        ],
        'source': {
            'type': 'path',
            'configuration': {
                'path': source_path,
            },
        },
        'target': {
            'type': 'path',
            'configuration': {
                'path': target_path,
            },
        },
    }
    if name:
        configuration_data['name'] = name

    if 'json' == format:
        file_path_extensions = FORMAT_JSON_EXTENSIONS
        formatter = json.dumps
    else:
        file_path_extensions = FORMAT_YAML_EXTENSIONS
        formatter = yaml.dump
    file_path_extensions_label = ', '.join(
        map(lambda x: '*.' + x, file_path_extensions))

    def _file_path_validator(path):
        if not any(map(path.endswith, file_path_extensions)):
            raise ValueError(
                'Configuration files must have %s extensions.' % file_path_extensions_label)
        return path

    saved = False
    while not saved:
        configuration_file_path = ask_any('Destination (%s)' % file_path_extensions_label,
                                          question='Where should backuppy store your new configuration file?',
                                          validator=_file_path_validator)
        try:
            with open(configuration_file_path, mode='w+t') as f:
                f.write(formatter(configuration_data))
            saved = True
        except BaseException as e:
            print(e)
    print('Your new back-up configuration has been saved. Start backing up your data by running the following command: backuppy -c %s' % configuration_file_path)


def main(args):
    """Provide the CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Backuppy backs up and restores your data using rsync.')
    add_commands_to_parser(parser)

    if args:
        parsed_args = parser.parse_args(args)
        try:
            parsed_args.func(parsed_args)
        except KeyboardInterrupt:
            # Quit gracefully.
            print('Quitting...')
        except BaseException:
            configuration = parsed_args.configuration
            configuration.logger.exception('A fatal error occurred.')
            configuration.notifier.alert(
                'A fatal error occurred. Details have been logged as per your configuration.')
    else:
        parser.print_help()
