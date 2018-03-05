"""Provide notifications."""
import subprocess


class Notifier:
    """Define a notifier."""

    def notify(self, message):
        """Send a notification.

        :param message: str
        """
        pass


class GroupedNotifiers(Notifier):
    """Define a notifier that groups other notifiers."""

    def __init__(self, notifiers):
        """Initialize a new instance.

        :param notifiers: Iterable[Notifier]
        """
        self._notifiers = notifiers

    def notify(self, message):
        """Send a notification.

        :param message: str
        """
        for notifier in self._notifiers:
            notifier.notify(message)


class NotifySendNotifier(Notifier):
    """Send notifications using the Linux notify-send utility.

    See https://linux.die.net/man/2/send.
    """

    def notify(self, message):
        """Send a notification.

        :param message: str
        """
        subprocess.call(('notify-send', "'%s'" % message))
