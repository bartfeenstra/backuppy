from unittest import TestCase

from paramiko import SSHException

from backuppy.config import Configuration
from backuppy.location import PathLocation, SshLocation

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class PathLocationTest(TestCase):
    def test_is_ready(self):
        path = '/var/cache'
        sut = PathLocation(path)
        self.assertTrue(sut.is_ready())

    def test_from_configuration_data(self):
        configuration = Mock(Configuration)
        path = '/var/cache'
        configuration_data = {
            'path': path,
        }
        sut = PathLocation.from_configuration_data(configuration, configuration_data)
        self.assertEquals(sut.path, path)

    def test_from_configuration_data_without_path(self):
        configuration = Mock(Configuration)
        configuration_data = {}
        with self.assertRaises(ValueError):
            PathLocation.from_configuration_data(configuration, configuration_data)


class SshLocationTest(TestCase):
    @patch('paramiko.SSHClient', autospec=True)
    def test_is_ready(self, m):
        configuration = Mock(Configuration)
        user = 'bart'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'host': host,
            'port': port,
            'path': path,
        }
        sut = SshLocation.from_configuration_data(configuration, configuration_data)
        self.assertTrue(sut.is_ready())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)

    @patch('paramiko.SSHClient', autospec=True)
    def test_is_ready_connection_error(self, m):
        m.return_value.connect = Mock(side_effect=SSHException)
        configuration = Mock(Configuration)
        user = 'bart'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'host': host,
            'port': port,
            'path': path,
        }
        sut = SshLocation.from_configuration_data(configuration, configuration_data)
        self.assertFalse(sut.is_ready())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)

    def test_from_configuration_data(self):
        configuration = Mock(Configuration)
        user = 'bart'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'host': host,
            'port': port,
            'path': path,
        }
        sut = SshLocation.from_configuration_data(configuration, configuration_data)
        self.assertEquals(sut.path, path)
        self.assertEquals(sut.user, user)
        self.assertEquals(sut.host, host)
        self.assertEquals(sut.port, port)

    def test_from_configuration_data_with_default_port(self):
        configuration = Mock(Configuration)
        user = 'bart'
        host = 'example.com'
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'host': host,
            'path': path,
        }
        sut = SshLocation.from_configuration_data(configuration, configuration_data)
        self.assertEquals(sut.port, 22)

    def test_from_configuration_data_without_user(self):
        configuration = Mock(Configuration)
        host = 'example.com'
        port = 666
        path = '/var/cache'
        configuration_data = {
            'host': host,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_configuration_data(configuration, configuration_data)

    def test_from_configuration_data_without_host(self):
        configuration = Mock(Configuration)
        user = 'bart'
        port = 666
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_configuration_data(configuration, configuration_data)

    def test_from_configuration_data_without_path(self):
        configuration = Mock(Configuration)
        user = 'bart'
        host = 'example.com'
        port = 666
        configuration_data = {
            'user': user,
            'host': host,
            'port': port,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_configuration_data(configuration, configuration_data)

    def test_from_configuration_data_with_invalid_port_too_low(self):
        configuration = Mock(Configuration)
        user = 'bart'
        host = 'example.com'
        port = -1
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'host': host,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_configuration_data(configuration, configuration_data)

    def test_from_configuration_data_with_invalid_port_too_high(self):
        configuration = Mock(Configuration)
        user = 'bart'
        host = 'example.com'
        port = 65536
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'host': host,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_configuration_data(configuration, configuration_data)
