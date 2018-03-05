"""Provide back-up locations."""


class Location:
    """Provide a backup location."""

    def is_ready(self):
        """Check if the target is ready to back up to.

        :return: bool
        """
        pass


class PathLocation(Location):
    """Provide a local, path-based backup location."""

    def __init__(self, path):
        """Initialize a new instance.

        :param path: str
        """
        self._path = path

    def is_ready(self):
        """Check if the target is ready to back up to.

        :return: bool
        """
        return True

    @classmethod
    def from_raw(cls, configuration_file_path, data):
        """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

        :param configuration_file_path: str
        :param data: dict
        :return: cls
        :raise: ValueError
        """
        if 'path' not in data:
            raise ValueError('`path` is required.')
        # @todo If path is relative, make absolute
        # @todo Check path exists
        # @todo Raise error otherwise
        path = data['path']
        return cls(path)

    @property
    def path(self):
        """Get the location's file path.

        :return: str
        """
        return self._path


class SshLocation(Location):
    """Provide a location over SSH."""

    def __init__(self, user, host, path, port=22):
        """Initialize a new instance.

        :param user: str
        :param host: str
        :param path: str
        :param port: int
        """
        self._user = user
        self._host = host
        self._port = port
        self._path = path

    @classmethod
    def from_raw(cls, configuration_file_path, data):
        """Parse configuration from raw, built-in types such as dictionaries, lists, and scalars.

        :param configuration_file_path: str
        :param data: dict
        :return: cls
        :raise: ValueError
        """
        kwargs = {}

        required_string_names = ('user', 'host', 'path')
        for required_string_name in required_string_names:
            if required_string_name not in data:
                raise ValueError('`%s` is required.' % required_string_name)
            kwargs[required_string_name] = data[required_string_name]

        if 'port' in data:
            if data['port'] < 0 or data['port'] > 65535:
                raise ValueError('`port` must be an integer ranging from 0 to 65535.')
            kwargs['port'] = data['port']

        return cls(**kwargs)

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
