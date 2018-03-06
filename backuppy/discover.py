"""Discover plugins."""

from backuppy.location import PathLocation, SshLocation
from backuppy.notifier import NotifySendNotifier


def discover_location_types():
    """Discover the available location types.

    :return: Dict
    """
    return {
        'path': lambda configuration, notifier, configuration_data: PathLocation.from_configuration_data(
            notifier, configuration.working_directory, configuration_data),
        'ssh': lambda configuration, notifier, configuration_data: SshLocation.from_configuration_data(notifier, configuration_data),
    }


def new_location(configuration, notifier, location_configuration):
    """Create a new location instance.

    :param configuration: Configuration
    :param notifier: Notifier
    :param location_configuration: Dict
    :return: Location
    :raise: ValueError
    """
    location_types = discover_location_types()
    if location_configuration.type not in location_types:
        raise ValueError('`Location type must be one of the following: %s, but `%s` was given.' % (
            ', '.join(location_types.keys()), location_configuration.type))
    return location_types[location_configuration.type](configuration, notifier, location_configuration.configuration_data)


def discover_notifier_types():
    """Discover the available notifier types.

    :return: Dict
    """
    return {
        'notify-send': lambda configuration, notifier, configuration_data: NotifySendNotifier(),
    }


def new_notifier(configuration, notifier, notifier_configuration):
    """Create a new notifier instance.

    :param configuration: Configuration
    :param notifier: Notifier
    :param notifier_configuration: Dict
    :return: Notifier
    :raise: ValueError
    """
    notifier_types = discover_notifier_types()
    if notifier_configuration.type not in notifier_types:
        raise ValueError('`Notifier type must be one of the following: %s, but `%s` was given.' % (
            ', '.join(notifier_types.keys()), notifier_configuration.type))
    return notifier_types[notifier_configuration.type](configuration, notifier, notifier_configuration.configuration_data)
