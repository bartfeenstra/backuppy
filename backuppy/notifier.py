"""Provide notifications."""
from __future__ import print_function

import subprocess
import sys


class Notifier:
    """Define a notifier."""

    def state(self, message):
        """Send a notification that may be ignored.

        :param message: str
        """
        pass

    def inform(self, message):
        """Send an informative notification.

        :param message: str
        """
        pass

    def confirm(self, message):
        """Send a confirmation/success notification.

        :param message: str
        """
        pass

    def alert(self, message):
        """Send an error notification.

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

    @property
    def notifiers(self):
        """Get the grouped notifiers.

        :return: Iterable[Notifier]
        """
        return self._notifiers

    def state(self, message):
        """Send a notification that may be ignored.

        :param message: str
        """
        for notifier in self._notifiers:
            notifier.state(message)

    def inform(self, message):
        """Send an informative notification.

        :param message: str
        """
        for notifier in self._notifiers:
            notifier.inform(message)

    def confirm(self, message):
        """Send a confirmation/success notification.

        :param message: str
        """
        for notifier in self._notifiers:
            notifier.confirm(message)

    def alert(self, message):
        """Send an error notification.

        :param message: str
        """
        for notifier in self._notifiers:
            notifier.alert(message)


class NotifySendNotifier(Notifier):
    """Send notifications using the Linux notify-send utility.

    See https://linux.die.net/man/2/send.
    """

    def _notify(self, message, urgency):
        """Send a notification.

        :param message: str
        """
        subprocess.call(('notify-send', '-c', 'backuppy', '-u', urgency, message))

    def state(self, message):
        """Send a notification that may be ignored.

        :param message: str
        """
        self._notify(message, 'low')

    def inform(self, message):
        """Send an informative notification.

        :param message: str
        """
        self._notify(message, 'normal')

    def confirm(self, message):
        """Send a confirmation/success notification.

        :param message: str
        """
        self._notify(message, 'normal')

    def alert(self, message):
        """Send an error notification.

        :param message: str
        """
        self._notify(message, 'critical')


class FileNotifier(Notifier):
    """Send notifications to files."""

    def __init__(self, state_file, inform_file, confirm_file, alert_file):
        """Initialize a new instance.

        :param state_file: File
        :param inform_file: File
        :param confirm_file: File
        :param alert_file: File
        """
        self._state_file = state_file
        self._inform_file = inform_file
        self._confirm_file = confirm_file
        self._alert_file = alert_file

    @classmethod
    def for_stdio(cls):
        """Get a new notifier for stdout and stderr.

        :return: cls
        """
        return cls(sys.stdout, sys.stdout, sys.stdout, sys.stderr)

    def _print(self, message, color, file):
        print('\033[0;%dm  \033[0;1;%dm %s\033[0m' % (color + 40, color + 30, message), file=file)

    def state(self, message):
        """Send a notification that may be ignored.

        :param message: str
        """
        self._print(message, 7, self._state_file)

    def inform(self, message):
        """Send an informative notification.

        :param message: str
        """
        self._print(message, 6, self._inform_file)

    def confirm(self, message):
        """Send a confirmation/success notification.

        :param message: str
        """
        self._print(message, 2, self._confirm_file)

    def alert(self, message):
        """Send an error notification.

        :param message: str
        """
        self._print(message, 1, self._alert_file)
