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


def _new_path_location_from_configuration_data(cls, configuration, configuration_data):
    """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

    :param configuration: Configuration
    :param configuration_data: dict
    :return: cls
    :raise: ValueError
    """
    if 'path' not in configuration_data:
        raise ValueError('`path` is required.')
    path_data = configuration_data['path']
    if '/' != path_data[0]:
        path_data = '%s/%s' % (configuration.working_directory, path_data)
    path = path_data

    return cls(configuration.logger, configuration.notifier, path)


def _discover_source_types():
    """Discover the available source types.

    :return: Dict
    """
    return {
        'path': partial(_new_path_location_from_configuration_data, PathSource),
    }


new_source = partial(_new, _discover_source_types())


def _new_ssh_target_from_configuration_data(configuration, configuration_data):
    """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

    :param notifier: Notifier
    :param configuration_data: dict
    :return: cls
    :raise: ValueError
    """
    kwargs = {}

    required_string_names = ('user', 'host', 'path')
    for required_string_name in required_string_names:
        if required_string_name not in configuration_data:
            raise ValueError('`%s` is required.' % required_string_name)
        kwargs[required_string_name] = configuration_data[required_string_name]

    if 'port' in configuration_data:
        if configuration_data['port'] < 0 or configuration_data['port'] > 65535:
            raise ValueError(
                '`port` must be an integer ranging from 0 to 65535.')
        kwargs['port'] = configuration_data['port']

    return SshTarget(configuration.notifier, **kwargs)


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
        targets.append(
            new_target(configuration, target_configuration_data['type'], target_configuration_data['configuration']))

    return FirstAvailableTarget(targets)


def _discover_target_types():
    """Discover the available target types.

    :return: Dict
    """
    return {
        'path': partial(_new_path_location_from_configuration_data, PathTarget),
        'ssh': _new_ssh_target_from_configuration_data,
        'first_available': _new_first_available_target_from_configuration_data,
    }


new_target = partial(_new, _discover_target_types())


def _new_command_notifier_from_configuration_data(configuration, configuration_data):
    """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

    :param configuration: Configuration
    :param configuration_data: dict
    :return: CommandNotifier
    :raise: ValueError
    """
    state_args = configuration_data['state'] if 'state' in configuration_data else None
    inform_args = configuration_data['inform'] if 'inform' in configuration_data else None
    confirm_args = configuration_data['confirm'] if 'confirm' in configuration_data else None
    alert_args = configuration_data['alert'] if 'alert' in configuration_data else None
    fallback_args = configuration_data['fallback'] if 'fallback' in configuration_data else None
    if None in [state_args, inform_args, confirm_args, alert_args] and fallback_args is None:
        raise ValueError(
            '`fallback` must be given if one or more of the other arguments are omitted.')

    return CommandNotifier(state_args, inform_args, confirm_args, alert_args, fallback_args)


def _new_file_notifier_from_configuration_data(configuration, configuration_data):
    """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

    :param configuration: Configuration
    :param configuration_data: dict
    :return: CommandNotifier
    :raise: ValueError
    """
    state_file = open(
        configuration_data['state'], mode='a+t') if 'state' in configuration_data else None
    inform_file = open(
        configuration_data['inform'], mode='a+t') if 'inform' in configuration_data else None
    confirm_file = open(
        configuration_data['confirm'], mode='a+t') if 'confirm' in configuration_data else None
    alert_file = open(
        configuration_data['alert'], mode='a+t') if 'alert' in configuration_data else None
    fallback_file = open(
        configuration_data['fallback'], mode='a+t') if 'fallback' in configuration_data else None
    if None in [state_file, inform_file, confirm_file, alert_file] and fallback_file is None:
        raise ValueError(
            '`fallback` must be given if one or more of the other arguments are omitted.')

    return FileNotifier(state_file, inform_file, confirm_file, alert_file, fallback_file)


def _discover_notifier_types():
    """Discover the available notifier types.

    :return: Dict
    """
    return {
        'notify-send': lambda configuration, configuration_data: NotifySendNotifier(),
        'command': _new_command_notifier_from_configuration_data,
        'stdio': lambda configuration, configuration_data: StdioNotifier(),
        'file': _new_file_notifier_from_configuration_data,
    }


new_notifier = partial(_new, _discover_notifier_types())
