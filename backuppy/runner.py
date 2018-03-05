"""Code to run back-ups."""

from backuppy.discover import discover_notifier_types, discover_location_types
from backuppy.location import FirstAvailableLocation
from backuppy.notifier import GroupedNotifiers, FileNotifier


class Runner:
    """The backup runner."""

    def __init__(self, configuration):
        """Initialize a new instance.

        :param configuration: Configuration
        """
        self._configuration = configuration

        notifier_types = discover_notifier_types()
        notifiers = [FileNotifier.for_stdio()]
        for notifier_configuration in configuration.notifiers:
            if notifier_configuration.type not in notifier_types:
                raise ValueError('`Notifier type must be one of the following: %s, but `%s` was given.' % (
                    ', '.join(notifier_types.keys()), notifier_configuration.type))
            notifiers.append(
                notifier_types[notifier_configuration.type](configuration, notifier_configuration.configuration_data))
        self._notifier = GroupedNotifiers(notifiers)

        location_types = discover_location_types()

        targets = []
        for target_configuration in configuration.targets:
            if target_configuration.type not in location_types:
                raise ValueError('`Location type must be one of the following: %s, but `%s` was given.' % (
                    ', '.join(location_types.keys()), target_configuration.type))
            targets.append(
                location_types[target_configuration.type](configuration, target_configuration.configuration_data))
        self._target = FirstAvailableLocation(targets)

    def backup(self):
        """Start a new back-up."""
        self._notifier.state('Initializing back-up %s' % self._configuration.name)

        if not self._target.is_available():
            self._notifier.alert('No back-up target available.')
            return None

        self._notifier.inform('Backing up %s...' % self._configuration.name)
