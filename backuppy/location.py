"""Provide back-up locations."""
import os
import socket
import subprocess
from binascii import b2a_hex
from time import strftime, gmtime

import paramiko
from paramiko import SSHException, RejectPolicy

from backuppy.cli.input import ask_confirm


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
        # If the given snapshot does not exist, prepopulate the new snapshot with an archived, linked, recursive copy of
        # the previous snapshot if it exists, or create a new, empty snapshot otherwise.
        ['bash', '-c', 'if [[ ! -d %s && -d latest ]]; then cp -al `readlink latest` %s; fi' %
         (name, name)],

        # Create the new snapshot directory if it does not exist.
        ['bash', '-c', 'if [ ! -d %s ]; then mkdir %s; fi' % (name, name)],

        # Re-link the `./latest` symlink.
        ['rm', '-f', 'latest'],
        ['ln', '-s', name, 'latest'],
    ]


class SshOptionsProvider(object):
    """Provide SSH options."""

    def ssh_options(self):
        """Build SSH options.

        :return: Dict[str, str]
        """
        return {
            'StrictHostKeyChecking': 'yes',
        }


class Location(object):
    """Provide a backup location."""

    def is_available(self):
        """Check if the target is available.

        :return: bool
        """
        raise NotImplementedError()  # pragma: no cover

    def to_rsync(self):
        """Build this location's rsync path.

        :return: str
        """
        raise NotImplementedError()  # pragma: no cover


class Source(Location):
    """Provide a backup source."""

    pass


class Target(Location):
    """Provide a backup target."""

    def snapshot(self, name):
        """Create a new snapshot.

        :param name: str
        """
        raise NotImplementedError()  # pragma: no cover


class PathLocation(Location):
    """Provide a local, path-based backup location."""

    def __init__(self, logger, notifier, path):
        """Initialize a new instance.

        :param logger: logging.Logger
        :param notifier: Notifier
        :param path: str
        """
        self._logger = logger
        self._notifier = notifier
        self._path = path

    def is_available(self):
        """Check if the target is available.

        :return: bool
        """
        if os.path.exists(self.path):
            return True
        message = 'Path `%s` does not exist.' % self._path
        self._logger.debug(message)
        self._notifier.alert(message)

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

        :return: strF
        """
        return self._path


class PathTarget(Target, PathLocation):
    """Provide a local, path-based back-up target."""

    def to_rsync(self):
        """Build this location's rsync path.

        :return: str
        """
        return '%s/%s' % (self._path.rstrip('/'), 'latest/')

    def snapshot(self, name):
        """Create a new snapshot.

        :param name: str
        """
        for args in _new_snapshot_args(name):
            subprocess.check_call(args, cwd=self._path)


class AskPolicy(RejectPolicy):
    """An SSH missing host key policy that interactively asks users whether to accept the key."""

    def missing_host_key(self, client, hostname, key):
        """Handle a missing host key."""
        fingerprint = b2a_hex(key.get_fingerprint()).decode('utf-8')
        fingerprint_label = ':'.join(
            [fingerprint[i:i + 2] for i in range(0, len(fingerprint), 2)])
        add = ask_confirm('Accept unknown host',
                          'Do you want to connect to previously unknown host %s using %s key %s?\nThe fact that this host is unknown can mean you have never connected to it before, its SSH server has been reconfigured, or it has been compromised.' % (
                              hostname, key.get_name(), fingerprint_label), False)
        if not add:
            RejectPolicy.missing_host_key(self, client, hostname, key)


class SshLocation(Location, SshOptionsProvider):
    """Provide a target over SSH."""

    def __init__(self, notifier, user, host, path, port=22, identity=None, host_keys=None, interactive=False):
        """Initialize a new instance.

        :param user: str
        :param host: str
        :param path: str
        :param port: int
        :param identity: Optional[str]
        :param host_keys: Optional[str]
        :param interactive: bool
        """
        self._notifier = notifier
        self._user = user
        self._host = host
        self._port = port
        self._path = path
        self._identity = identity
        self._host_keys = host_keys
        self._interactive = interactive

    def is_available(self):
        """Check if the target is available.

        :return: bool
        """
        try:
            with self._connect():
                return True
        except SSHException as e:
            self._notifier.alert(
                'Could not establish an SSH connection to the remote: %s.' % str(e))
            return False
        except socket.timeout:
            self._notifier.alert('The remote timed out.')
            return False

    def _connect(self):
        """Connect to the remote.

        :return: paramiko.SSHClient
        """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        if self._host_keys:
            client.load_host_keys(self._host_keys)
        if self._interactive:
            client.set_missing_host_key_policy(AskPolicy())
        else:
            client.set_missing_host_key_policy(RejectPolicy())
        connect_args = {}
        if self._identity:
            connect_args['look_for_keys'] = False
            connect_args['key_filename'] = self._identity
        client.connect(self._host, self._port, self._user,
                       timeout=9, **connect_args)
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

    def ssh_options(self):
        """Build SSH options.

        :return: Dict[str, str]
        """
        options = SshOptionsProvider.ssh_options(self)
        options['Port'] = str(self.port)
        options['UserKnownHostsFile'] = self._host_keys
        options['IdentityFile'] = self._identity
        return options


class SshSource(Source, SshLocation):
    """Provide a source over SSH."""

    def to_rsync(self):
        """Build this location's rsync path.

        :return: str
        """
        return '%s@%s:%s/' % (self.user, self.host, self._path.rstrip('/'))


class SshTarget(Target, SshLocation):
    """Provide a target over SSH."""

    def snapshot(self, name):
        """Create a new snapshot.

        :param name: str
        """
        with self._connect() as client:
            for args in _new_snapshot_args(name):
                client.exec_command(' '.join(args))

    def to_rsync(self):
        """Build this location's rsync path.

        :return: str
        """
        return '%s@%s:%s/latest/' % (self.user, self.host, self._path.rstrip('/'))


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

    def snapshot(self, name):
        """Create a new snapshot.

        :param name: str
        """
        return self._get_available_target().snapshot(name)

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
