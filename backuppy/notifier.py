"""Provide notifications."""
import subprocess


class Notifier:
    """Define a notifier."""

    def notify(self, message):
        """Send a notification.

        :param message: str
        """
        pass


class NotifySendNotifier(Notifier):
    """Send notifications using the Linux notify-send utility.

    See https://linux.die.net/man/2/send.
    """

    @classmethod
    def from_raw(cls, configuration_file_path, data):
        """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

        :param configuration_file_path: str
        :param data: dict
        :return: cls
        :raise: ValueError
        """
        return cls()

    def notify(self, message):
        """Send a notification.

        :param message: str
        """
        subprocess.call(('notify-send', "'%s'" % message))
