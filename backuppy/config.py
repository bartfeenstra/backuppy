"""Provides configuration components."""
import json
import logging
import os
from logging import config as logging_config

import yaml

from backuppy.location import Source, Target
from backuppy.notifier import GroupedNotifiers, Notifier, QuietNotifier
from backuppy.plugin import new_source, new_target, new_notifier


class Configuration(object):
    """Provides back-up configuration."""

    def __init__(self, name, working_directory=None, verbose=False):
        """Initialize a new instance.

        :param name: str
        :param logger: logging.Logger
        :param working_directory: str
        :param verbose: bool
        """
        self._name = name
        self._working_directory = working_directory
        self._verbose = verbose
        self._source = None
        self._target = None
        self._notifier = None
        self._logger = logging.getLogger('backuppy')

    @property
    def verbose(self):
        """Get output verbosity.

        :return: bool
        """
        return self._verbose

    @verbose.setter
    def verbose(self, verbose):
        """Set output verbosity.

        :param verbose: bool
        """
        self._verbose = verbose

    @property
    def name(self):
        """Get the back-up's name.

        :return: str
        """
        return self._name

    @property
    def working_directory(self):
        """Get the working directory.

        :return: str
        """
        if self._working_directory is None:
            raise AttributeError('No working directory has been set.')

        return self._working_directory

    @property
    def notifier(self):
        """Get the notifier.

        :return: Notifier
        """
        if self._notifier is None:
            raise AttributeError('No notifier has been set.')

        return self._notifier

    @notifier.setter
    def notifier(self, notifier):
        """Set the notifier.

        :param notifier: Notifier
        """
        assert isinstance(notifier, Notifier)
        if self._notifier is not None:
            raise AttributeError('A notifier has already been set.')
        self._notifier = notifier

    @property
    def source(self):
        """Get the back-up source.

        :return: Source
        """
        if self._source is None:
            raise AttributeError('No source has been set.')

        return self._source

    @source.setter
    def source(self, source):
        """Set the back-up source.

        :param source: source
        """
        assert isinstance(source, Source)
        if self._source is not None:
            raise AttributeError('A source has already been set.')
        self._source = source

    @property
    def target(self):
        """Get the back-up target.

        :return: Target
        """
        if self._target is None:
            raise AttributeError('No target has been set.')

        return self._target

    @target.setter
    def target(self, target):
        """Set the back-up target.

        :param target: target
        """
        assert isinstance(target, Target)
        if self._target is not None:
            raise AttributeError('A target has already been set.')
        self._target = target

    @property
    def logger(self):
        """Get the logger.

        :return: logging.Logger
        """
        return self._logger


def from_configuration_data(configuration_file_path, data, verbose=None):
    """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

    :param configuration_file_path: str
    :param data: dict
    :param verbose: Optional[bool]
    :return: cls
    :raise: ValueError
    """
    name = data['name'] if 'name' in data else configuration_file_path
    working_directory = os.path.dirname(configuration_file_path)
    if verbose is None and 'verbose' in data:
        if not isinstance(data['verbose'], bool):
            raise ValueError('`verbose` must be a boolean.')
        verbose = data['verbose']
    configuration = Configuration(name, working_directory, verbose)

    if 'logging' in data:
        logging_config.dictConfig(data['logging'])

    notifier = GroupedNotifiers()
    if 'notifications' in data:
        for notifier_data in data['notifications']:
            if 'type' not in notifier_data:
                raise ValueError('`notifiers[][type]` is required.')
            notifier_configuration = notifier_data['configuration'] if 'configuration' in notifier_data else None
            notifier.notifiers.append(new_notifier(
                configuration, notifier_data['type'], notifier_configuration))
    if not configuration.verbose:
        notifier = QuietNotifier(notifier)
    configuration.notifier = notifier

    if 'source' not in data:
        raise ValueError('`source` is required.')
    if 'type' not in data['source']:
        raise ValueError('`source[type]` is required.')
    source_configuration = data['source']['configuration'] if 'configuration' in data['source'] else None
    configuration.source = new_source(
        configuration, data['source']['type'], source_configuration)

    if 'target' not in data:
        raise ValueError('`target` is required.')
    if 'type' not in data['target']:
        raise ValueError('`target[type]` is required.')
    target_configuration = data['target']['configuration'] if 'configuration' in data['target'] else None
    configuration.target = new_target(
        configuration, data['target']['type'], target_configuration)

    return configuration


def from_json(f, verbose=None):
    """Parse configuration from a JSON file.

    :param f: File
    :param verbose: Optional[bool]
    :return: Configuration
    """
    return from_configuration_data(f.name, json.load(f), verbose=verbose)


def from_yaml(f, verbose=None):
    """Parse configuration from a YAML file.

    :param f: File
    :param verbose: Optional[bool]
    :return: Configuration
    """
    return from_configuration_data(f.name, yaml.load(f), verbose=verbose)
