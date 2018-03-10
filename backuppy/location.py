"""Provide back-up locations."""
import abc
import os
import socket
import subprocess
from abc import ABCMeta
from time import strftime, gmtime

import paramiko
import six
from paramiko import SSHException


def new_snapshot_name():
    """Build the name for a new back-up snapshot.

    :return: str
    """
    return strftime('%Y-%m-%d_%H-%M-%S_UTC', gmtime())


def _new_snapshot_args(name):
    """Build the cli arguments to create a back-up snapshot.

    :return: Iterable[Iterable[str]]
    """
    return [
        ['mkdir', name],
        ['rm', '-f', 'latest'],
        ['ln', '-s', name, 'latest'],
    ]


class Location(six.with_metaclass(ABCMeta), object):
    """Provide a backup location."""

    @abc.abstractmethod
    def is_available(self):
        """Check if the target is available.

        :return: bool
        """
        pass

    @abc.abstractmethod
    def to_rsync(self):
        """Build this location's rsync path.

        :return: str
        """
        pass


class Source(Location):
    """Provide a backup source."""

    pass


class Target(Location):
    """Provide a backup target."""

    @abc.abstractmethod
    def snapshot(self):
        """Create a new snapshot."""
        pass


class PathLocation(Location):
    """Provide a local, path-based backup location."""

    def __init__(self, notifier, path):
        """Initialize a new instance.

        :param notifier: Notifier
        :param path: str
        """
        self._notifier = notifier
        self._path = path

    def is_available(self):
        """Check if the target is available.

        :return: bool
        """
        if os.path.exists(self.path):
            return True
        self._notifier.alert('Path `%s` does not exist.' % self._path)

    @property
    def path(self):
        """Get the location's file path.

        :return: str
        """
        return self._path


class PathSource(Source, PathLocation):
    """Provide a local, path-based back-up source."""

    def to_rsync(self):
        """Build this location's rsync path.

        :return: str
        """
        return self._path


class PathTarget(Target, PathLocation):
    """Provide a local, path-based back-up target."""

    def to_rsync(self):
        """Build this location's rsync path.

        :return: str
        """
        return '/'.join([self.path, 'latest'])

    def snapshot(self):
        """Create a new snapshot."""
        snapshot_name = new_snapshot_name()
        for args in _new_snapshot_args(snapshot_name):
            code = subprocess.call(args, cwd=self._path)
            if 0 != code:
                raise RuntimeError('Could not create snapshot at %s.' % self._path)


class SshTarget(Target):
    """Provide a target over SSH."""

    def __init__(self, notifier, user, host, path, port=22):
        """Initialize a new instance.

        :param user: str
        :param host: str
        :param path: str
        :param port: int
        """
        self._notifier = notifier
        self._user = user
        self._host = host
        self._port = port
        self._path = path

    def is_available(self):
        """Check if the target is available.

        :return: bool
        """
        try:
            self._connect()
            return True
        except SSHException:
            self._notifier.alert('Could not establish an SSH connection to the remote.')
            return False
        except socket.timeout:
            self._notifier.alert('The remote timed out.')
            return False

    def snapshot(self):
        """Create a new snapshot."""
        snapshot_name = new_snapshot_name()
        with self._connect() as client:
            for args in _new_snapshot_args(snapshot_name):
                client.exec_command(' '.join(args))

    def _connect(self):
        """Connect to the remote.

        :return: paramiko.SSHClient
        """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())
        client.connect(self._host, self._port, self._user, timeout=9)
        return client

    @property
    def path(self):
        """Get the location's absolute file path on the remote host.

        :return: str
        """
        return self._path

    @property
    def user(self):
        """Get the location's user.

        :return: str
        """
        return self._user

    @property
    def host(self):
        """Get the location's host.

        :return: str
        """
        return self._host

    @property
    def port(self):
        """Get the location's SSH port.

        :return: int
        """
        return self._port

    def to_rsync(self):
        """Build this location's rsync path.

        :return: str
        """
        return '%s@%s:%d/%s/latest' % (self.user, self.host, self.port, self.path)


class FirstAvailableTarget(Target):
    """A target that decorates the first available of the given targets."""

    def __init__(self, targets):
        """Initialize a new instance.

        :param targets: Iterable[Target]
        """
        self._targets = targets
        self._available_target = None

    def is_available(self):
        """Check if the target is available.

        :return: bool
        """
        return self._get_available_target() is not None

    def to_rsync(self):
        """Build this location's rsync path.

        :return: str
        """
        return self._get_available_target().to_rsync()

    def snapshot(self):
        """Create a new snapshot."""
        return self._get_available_target().snapshot()

    def _get_available_target(self):
        """Get the first available target.

        :return: Optional[Target]
        """
        if self._available_target is not None:
            return self._available_target

        for target in self._targets:
            if target.is_available():
                self._available_target = target
                return target
