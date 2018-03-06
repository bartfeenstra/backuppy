"""Provide back-up locations."""
import os
import socket

import paramiko
from paramiko import SSHException


class Location:
    """Provide a backup location."""

    def is_available(self):
        """Check if the target is available.

        :return: bool
        """
        pass

    def to_rsync(self):
        """Build this location's rsync path.

        :return: str
        """
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

    @classmethod
    def from_configuration_data(cls, notifier, working_directory, configuration_data):
        """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

        :param working_directory: str
        :param configuration_data: dict
        :return: cls
        :raise: ValueError
        """
        if 'path' not in configuration_data:
            raise ValueError('`path` is required.')
        path_data = configuration_data['path']
        if '/' != path_data[0]:
            path_data = '%s/%s' % (working_directory, path_data)
        path = path_data

        return cls(notifier, path)

    @property
    def path(self):
        """Get the location's file path.

        :return: str
        """
        return self._path

    def to_rsync(self):
        """Build this location's rsync path.

        :return: str
        """
        return self.path


class SshLocation(Location):
    """Provide a location over SSH."""

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

    def _connect(self):
        """Connect to the remote.

        :return: paramiko.SSHClient
        """
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())
        client.connect(self._host, self._port, self._user, timeout=9)
        return client

    @classmethod
    def from_configuration_data(cls, notifier, configuration_data):
        """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

        :param notifier: Notifier
        :param configuration_data: dict
        :return: cls
        :raise: ValueError
        """
        kwargs = {}

        required_string_names = ('user', 'host', 'path')
        for required_string_name in required_string_names:
            if required_string_name not in configuration_data:
                raise ValueError('`%s` is required.' % required_string_name)
            kwargs[required_string_name] = configuration_data[required_string_name]

        if 'port' in configuration_data:
            if configuration_data['port'] < 0 or configuration_data['port'] > 65535:
                raise ValueError('`port` must be an integer ranging from 0 to 65535.')
            kwargs['port'] = configuration_data['port']

        return cls(notifier, **kwargs)

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
        return '%s@%s:%d/%s' % (self.user, self.host, self.port, self.path)


class FirstAvailableLocation(Location):
    """A location that decorates the first available of the given locations."""

    def __init__(self, locations=None):
        """Initialize a new instance.

        :param locations: Iterable[Location]
        """
        self._locations = locations if locations is not None else []
        self._available_location = None

    @property
    def locations(self):
        """Get the configured locations.

        :return: Iterable[Location]
        """
        return self._locations

    def is_available(self):
        """Check if the target is available.

        :return: bool
        """
        return self._get_available_location() is not None

    def _get_available_location(self):
        """Get the first available location.

        :return: Optional[Location]
        """
        if self._available_location is not None:
            return self._available_location

        for location in self._locations:
            if location.is_available():
                self._available_location = location
                return location
