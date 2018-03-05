"""Code to run back-ups."""

from backuppy.discover import discover_notifier_types
from backuppy.notifier import GroupedNotifiers


class Runner:
    """The backup runner."""

    def __init__(self, configuration):
        """Initialize a new instance.

        :param configuration: Configuration
        """
        self._configuration = configuration
        notifier_types = discover_notifier_types()
        notifiers = []
        for notifier_configuration in configuration.notifiers:
            if notifier_configuration.type not in notifier_types:
                raise ValueError('`Notifier must be one of the following: %s, but `%s` was given.' % (
                    ', '.join(notifier_types.keys()), notifier_configuration.type))
            notifiers.append(
                notifier_types[notifier_configuration.type](configuration, notifier_configuration.configuration_data))
        self._notifier = GroupedNotifiers(notifiers)

    def backup(self):
        """Start a new back-up."""
        self._notifier.notify('Backing up %s...' % self._configuration.name)
