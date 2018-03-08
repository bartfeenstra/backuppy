"""Discover plugins."""
from functools import partial

from backuppy.location import PathSource, PathTarget, SshTarget
from backuppy.notifier import NotifySendNotifier, CommandNotifier, FileNotifier, StdioNotifier


def _new(plugin_types, configuration, notifier, plugin_configuration):
    """Create a new plugin instance.

    :param plugin_types: Iterable
    :param configuration: Configuration
    :param notifier: Notifier
    :param plugin_configuration: Dict
    :return: Any
    :raise: ValueError
    """
    if plugin_configuration.type not in plugin_types:
        raise ValueError('`Type must be one of the following: %s, but `%s` was given.' % (
            ', '.join(plugin_types.keys()), plugin_configuration.type))
    return plugin_types[plugin_configuration.type](configuration, notifier,
                                                   plugin_configuration.configuration_data)


def discover_source_types():
    """Discover the available source types.

    :return: Dict
    """
    return {
        'path': lambda configuration, notifier, configuration_data: PathSource.from_configuration_data(
            notifier, configuration.working_directory, configuration_data),
    }


new_source = partial(_new, discover_source_types())


def discover_target_types():
    """Discover the available target types.

    :return: Dict
    """
    return {
        'path': lambda configuration, notifier, configuration_data: PathTarget.from_configuration_data(
            notifier, configuration.working_directory, configuration_data),
        'ssh': lambda configuration, notifier, configuration_data: SshTarget.from_configuration_data(notifier,
                                                                                                     configuration_data),
    }


new_target = partial(_new, discover_target_types())


def discover_notifier_types():
    """Discover the available notifier types.

    :return: Dict
    """
    return {
        'notify-send': lambda configuration, notifier, configuration_data: NotifySendNotifier(),
        'command': lambda configuration, notifier, configuration_data: CommandNotifier.from_configuration_data(
            configuration_data),
        'stdio': lambda configuration, notifier, configuration_data: StdioNotifier(),
        'file': lambda configuration, notifier, configuration_data: FileNotifier.from_configuration_data(
            configuration_data),
    }


new_notifier = partial(_new, discover_notifier_types())
