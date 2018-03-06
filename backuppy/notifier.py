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
            raise ValueError('fallback_args must be given if one or more of the other arguments are omitted.')
        self._state_args = state_args
        self._inform_args = inform_args
        self._confirm_args = confirm_args
        self._alert_args = alert_args
        self._fallback_args = fallback_args

    @classmethod
    def from_configuration_data(cls, configuration_data):
        """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

        :param configuration_data: dict
        :return: cls
        :raise: ValueError
        """
        state_args = configuration_data['state'] if 'state' in configuration_data else None
        inform_args = configuration_data['inform'] if 'inform' in configuration_data else None
        confirm_args = configuration_data['confirm'] if 'confirm' in configuration_data else None
        alert_args = configuration_data['alert'] if 'alert' in configuration_data else None
        fallback_args = configuration_data['fallback'] if 'fallback' in configuration_data else None
        if None in [state_args, inform_args, confirm_args, alert_args] and fallback_args is None:
            raise ValueError('`fallback` must be given if one or more of the other arguments are omitted.')

        return cls(state_args, inform_args, confirm_args, alert_args, fallback_args)

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
