"""Discover plugins."""

from backuppy.location import PathLocation, SshLocation
from backuppy.notifier import NotifySendNotifier


def discover_location_types():
    """Discover the available location types.

    :return: Dict
    """
    return {
        'path': lambda configuration, configuration_data: PathLocation.from_configuration_data(
            configuration.working_directory, configuration_data),
        'ssh': lambda configuration, configuration_data: SshLocation.from_configuration_data(configuration_data),
    }


def discover_notifier_types():
    """Discover the available notifier types.

    :return: Dict
    """
    return {
        'notify-send': lambda configuration, configuration_data: NotifySendNotifier(),
    }
