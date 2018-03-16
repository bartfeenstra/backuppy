"""Provide notifications."""
from __future__ import print_function

import subprocess
import sys
from abc import ABCMeta

from six import with_metaclass


class Notifier(with_metaclass(ABCMeta), object):
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

    def __init__(self, notifiers=None):
        """Initialize a new instance.

        :param notifiers: Iterable[Notifier]
        """
        self._notifiers = notifiers if notifiers is not None else []

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


class CommandNotifier(Notifier):
    """Send notifications as shell commands using a subprocess."""

    def __init__(self, state_args=None, inform_args=None, confirm_args=None, alert_args=None, fallback_args=None):
        """Initialize a new instance.

        :param state_args: Optional[Iterable[str]]
        :param inform_args: Optional[Iterable[str]]
        :param confirm_args: Optional[Iterable[str]]
        :param alert_args: Optional[Iterable[str]]
        :param fallback_args: Optional[Iterable[str]]
        """
        if None in [state_args, inform_args, confirm_args, alert_args] and fallback_args is None:
            raise ValueError(
                'fallback_args must be given if one or more of the other arguments are omitted.')
        self._state_args = state_args
        self._inform_args = inform_args
        self._confirm_args = confirm_args
        self._alert_args = alert_args
        self._fallback_args = fallback_args

    def _call(self, args, message):
        """Send a notification.

        :param message: str
        """
        if args is None:
            args = self._fallback_args
        args = map(lambda x: x.replace('{message}', message), args)
        # Convert to a list so we can easily assert invocations.
        subprocess.call(list(args))

    def state(self, message):
        """Send a notification that may be ignored.

        :param message: str
        """
        self._call(self._state_args, message)

    def inform(self, message):
        """Send an informative notification.

        :param message: str
        """
        self._call(self._inform_args, message)

    def confirm(self, message):
        """Send a confirmation/success notification.

        :param message: str
        """
        self._call(self._confirm_args, message)

    def alert(self, message):
        """Send an error notification.

        :param message: str
        """
        self._call(self._alert_args, message)


class NotifySendNotifier(CommandNotifier):
    """Send notifications using the Linux notify-send utility.

    See https://linux.die.net/man/2/send.
    """

    def __init__(self):
        """Initialize a new instance."""
        args = ['notify-send', '-c', 'backuppy', '-u']
        CommandNotifier.__init__(self, args + ['low', '{message}'], args + ['normal', '{message}'],
                                 args + ['normal', '{message}'], args + ['critical', '{message}'])


class FileNotifier(Notifier):
    """Send notifications to files."""

    def __init__(self, state_file=None, inform_file=None, confirm_file=None, alert_file=None, fallback_file=None):
        """Initialize a new instance.

        :param state_file: Optional[Iterable[str]]
        :param inform_file: Optional[Iterable[str]]
        :param confirm_file: Optional[Iterable[str]]
        :param alert_file: Optional[Iterable[str]]
        :param fallback_file: Optional[Iterable[str]]
        """
        if None in [state_file, inform_file, confirm_file, alert_file] and fallback_file is None:
            raise ValueError(
                'fallback_file must be given if one or more of the other arguments are omitted.')
        self._state_file = state_file
        self._inform_file = inform_file
        self._confirm_file = confirm_file
        self._alert_file = alert_file
        self._fallback_file = fallback_file

    def _print(self, message, file=None):
        if file is None:
            file = self._fallback_file
        print(message, file=file)

    def state(self, message):
        """Send a notification that may be ignored.

        :param message: str
        """
        self._print(message, self._state_file)

    def inform(self, message):
        """Send an informative notification.

        :param message: str
        """
        self._print(message, self._inform_file)

    def confirm(self, message):
        """Send a confirmation/success notification.

        :param message: str
        """
        self._print(message, self._confirm_file)

    def alert(self, message):
        """Send an error notification.

        :param message: str
        """
        self._print(message, self._alert_file)


class StdioNotifier(Notifier):
    """Send notifications to stdout and stderr."""

    def _print(self, message, color, file=None):
        if file is None:
            file = sys.stdout
        print('\033[0;%dm  \033[0;1;%dm %s\033[0m' %
              (color + 40, color + 30, message), file=file)

    def state(self, message):
        """Send a notification that may be ignored.

        :param message: str
        """
        self._print(message, 7)

    def inform(self, message):
        """Send an informative notification.

        :param message: str
        """
        self._print(message, 6)

    def confirm(self, message):
        """Send a confirmation/success notification.

        :param message: str
        """
        self._print(message, 2)

    def alert(self, message):
        """Send an error notification.

        :param message: str
        """
        self._print(message, 1, sys.stderr)


class QuietNotifier(Notifier):
    """Provide a quiet notifier that only lets alerts pass through."""

    def __init__(self, notifier):
        """Initialize a new instance.

        :param notifier: Notifier
        """
        self._notifier = notifier

    def alert(self, message):
        """Send an error notification.

        :param message: str
        """
        self._notifier.alert(message)
