"""Discover plugins."""

from backuppy.location import PathLocation, SshLocation
from backuppy.notifier import NotifySendNotifier


def discover_location_types():
    """Discover the available location types.

    :return: Dict
    """
    return {
        'path': PathLocation.from_raw,
        'ssh': SshLocation.from_raw,
    }


def discover_notifier_types():
    """Discover the available notifier types.

    :return: Dict
    """
    return {
        'notify-send': NotifySendNotifier.from_raw,
    }
