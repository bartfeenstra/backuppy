"""Discover plugins."""
from functools import partial

from backuppy.location import PathSource, PathTarget, SshTarget, FirstAvailableTarget
from backuppy.notifier import NotifySendNotifier, CommandNotifier, FileNotifier, StdioNotifier


def _new(available_plugin_types, configuration, plugin_type, plugin_configuration_data=None):
    """Create a new plugin instance.

    :param available_plugin_types: Iterable
    :param configuration: Configuration
    :param plugin_type: str
    :param plugin_configuration_data: Dict
    :return: Any
    :raise: ValueError
    """
    if plugin_type not in available_plugin_types:
        raise ValueError('`Type must be one of the following: %s, but `%s` was given.' % (
            ', '.join(available_plugin_types.keys()), plugin_type))
    return available_plugin_types[plugin_type](configuration, plugin_configuration_data)


def discover_source_types():
    """Discover the available source types.

    :return: Dict
    """
    return {
        'path': lambda configuration, configuration_data: PathSource.from_configuration_data(configuration.notifier,
                                                                                             configuration.working_directory,
                                                                                             configuration_data),
    }


new_source = partial(_new, discover_source_types())


def _new_first_available_target_from_configuration_data(configuration, configuration_data):
    """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

    :param configuration: Configuration
    :param configuration_data: dict
    :return: cls
    :raise: ValueError
    """
    targets = []
    for target_configuration_data in configuration_data['targets']:
        target_configuration_data.setdefault('configuration')
        targets.append(new_target(configuration, target_configuration_data['type'], target_configuration_data['configuration']))

    return FirstAvailableTarget(targets)


def discover_target_types():
    """Discover the available target types.

    :return: Dict
    """
    return {
        'path': lambda configuration, configuration_data: PathTarget.from_configuration_data(configuration.notifier,
                                                                                             configuration.working_directory,
                                                                                             configuration_data),
        'ssh': lambda configuration, configuration_data: SshTarget.from_configuration_data(configuration.notifier,
                                                                                           configuration_data),
        'first_available': _new_first_available_target_from_configuration_data,
    }


new_target = partial(_new, discover_target_types())


def discover_notifier_types():
    """Discover the available notifier types.

    :return: Dict
    """
    return {
        'notify-send': lambda configuration, configuration_data: NotifySendNotifier(),
        'command': lambda configuration, configuration_data: CommandNotifier.from_configuration_data(
            configuration_data),
        'stdio': lambda configuration, configuration_data: StdioNotifier(),
        'file': lambda configuration, configuration_data: FileNotifier.from_configuration_data(configuration_data),
    }


new_notifier = partial(_new, discover_notifier_types())
