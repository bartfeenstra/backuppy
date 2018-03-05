"""Provides configuration components."""
import json
import os


class PluginConfiguration:
    """Defines a plugin and its configuration."""

    def __init__(self, plugin_type, configuration_data):
        """Initialize a new instance.

        :param plugin_type: str
        :param configuration_data: Dict
        """
        self._type = plugin_type
        self._configuration_data = configuration_data

    @property
    def type(self):
        """Get the plugin type.

        :return: str
        """
        return self._type

    @property
    def configuration_data(self):
        """Get the plugin's configuration data.

        :return: Dict
        """
        return self._configuration_data


class Configuration:
    """Provides back-up configuration."""

    def __init__(self, configuration_file_path, source, targets, name=None, verbose=False, notifiers=None):
        """Initialize a new instance.

        :param configuration_file_path: str
        :param source: PluginConfiguration
        :param targets: Iterable[PluginConfiguration]
        :param verbose: bool
        :param notifiers: Iterable[PluginConfiguration]
        """
        assert isinstance(source, PluginConfiguration)
        self._source = source
        assert len(targets) > 0
        for target in targets:
            assert isinstance(target, PluginConfiguration)
        self._targets = targets
        self._verbose = verbose
        if notifiers is not None:
            for notifier in notifiers:
                assert isinstance(notifier, PluginConfiguration)
            self._notifiers = notifiers
        else:
            self._notifiers = []
        assert os.path.exists(configuration_file_path) and os.path.isfile(configuration_file_path)
        self._configuration_file_path = configuration_file_path
        self._name = name

    @classmethod
    def from_configuration_data(cls, configuration_file_path, data):
        """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

        :param configuration_file_path: str
        :param data: dict
        :return: cls
        :raise: ValueError
        """
        kwargs = {}

        if 'verbose' in data:
            if not isinstance(data['verbose'], bool):
                raise ValueError('`verbose` must be a boolean.')
            kwargs['verbose'] = data['verbose']

        if 'source' not in data:
            raise ValueError('`source` is required.')
        if 'type' not in data['source']:
            raise ValueError('`source[type]` is required.')
        source = PluginConfiguration(data['source']['type'], data['source'])

        targets = []
        if 'targets' not in data:
            raise ValueError('`targets` is required.')
        for target_data in data['targets']:
            if 'type' not in target_data:
                raise ValueError('`targets[][type]` is required.')
            targets.append(PluginConfiguration(target_data['type'], target_data))

        notifiers = []
        if 'notifications' in data:
            for notifier_data in data['notifications']:
                if 'type' not in notifier_data:
                    raise ValueError('`notifiers[][type]` is required.')
                notifiers.append(PluginConfiguration(notifier_data['type'], notifier_data))
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
    return Configuration.from_configuration_data(f.name, json.load(f))