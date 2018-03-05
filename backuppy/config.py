"""Provides configuration components."""
import json

import os

from backuppy.discover import discover_notifier_types, discover_location_types
from backuppy.location import Location


class Configuration:
    """Provides back-up configuration."""

    def __init__(self, configuration_file_path, source, targets, name=None, verbose=False, notifiers=None):
        """Initialize a new instance.

        :param configuration_file_path: str
        :param source: Location
        :param targets: Iterable[Location]
        :param verbose: bool
        :param notifiers: Iterable[Notifier]
        """
        assert isinstance(source, Location)
        self._source = source
        assert len(targets) > 0
        for target in targets:
            assert isinstance(target, Location)
        self._targets = targets
        self._verbose = verbose
        self._notifiers = notifiers if notifiers is not None else []
        assert os.path.exists(configuration_file_path) and os.path.isfile(configuration_file_path)
        self._configuration_file_path = configuration_file_path
        self._name = name

    @classmethod
    def from_raw(cls, configuration_file_path, data):
        """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

        :param configuration_file_path: str
        :param data: dict
        :return: cls
        :raise: ValueError
        """
        kwargs = {}

        location_types = discover_location_types()
        notifier_types = discover_notifier_types()

        if 'verbose' in data:
            if not isinstance(data['verbose'], bool):
                raise ValueError('`verbose` must be a boolean.')
            kwargs['verbose'] = data['verbose']

        if 'source' not in data:
            raise ValueError('`source` is required.')
        if 'type' not in data['source']:
            raise ValueError('`source[type]` is required.')
        if data['source']['type'] not in location_types:
            raise ValueError('`source[type] must be one of the following: %s' % ', '.join(location_types.keys()))
        source = location_types[data['source']['type']](configuration_file_path, data['source'])

        targets = []
        if 'targets' not in data:
            raise ValueError('`targets` is required.')
        for target_data in data['targets']:
            if 'type' not in target_data:
                raise ValueError('`targets[][type]` is required.')
            if target_data['type'] not in location_types:
                raise ValueError('`targets[][type] must be one of the following: %s' % ', '.join(location_types.keys()))
            targets.append(location_types[target_data['type']](configuration_file_path, target_data))

        notifiers = []
        if 'notifications' in data:
            for notifier_data in data['notifications']:
                if 'type' not in notifier_data:
                    raise ValueError('`notifiers[][type]` is required.')
                if notifier_data['type'] not in notifier_types:
                    raise ValueError('`notifiers[][type] must be one of the following: %s' % ', '.join(notifier_types.keys()))
                notifiers.append(notifier_types[notifier_data['type']](configuration_file_path, notifier_data))
        kwargs['notifiers'] = notifiers

        return cls(configuration_file_path, source, targets, **kwargs)

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
        return self._name if self._name else self.working_directory

    @property
    def working_directory(self):
        """Get the working directory.

        :return: str
        """
        return os.path.dirname(self._configuration_file_path)

    @property
    def notifiers(self):
        """Get the notifiers.

        :return: Iterable[Notifier]
        """
        return self._notifiers


def from_json(f):
    """Parse configuration from a JSON file.

    :param f: File
    :return: Configuration
    """
    return Configuration.from_raw(f.name, json.load(f))
