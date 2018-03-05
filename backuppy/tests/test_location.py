import socket
from unittest import TestCase

from paramiko import SSHException

from backuppy.config import Configuration
from backuppy.location import PathLocation, SshLocation, FirstAvailableLocation

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class PathLocationTest(TestCase):
    def test_is_available(self):
        path = '/tmp'
        sut = PathLocation(path)
        self.assertTrue(sut.is_available())

    def test_is_available_unavailable(self):
        path = '/tmp/SomeNoneExistentPath'
        sut = PathLocation(path)
        self.assertFalse(sut.is_available())

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
    def test_is_available(self, m):
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
        sut = SshLocation.from_configuration_data(configuration_data)
        self.assertTrue(sut.is_available())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)

    @patch('paramiko.SSHClient', autospec=True)
    def test_is_available_connection_error(self, m):
        m.return_value.connect = Mock(side_effect=SSHException)
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
        sut = SshLocation.from_configuration_data(configuration_data)
        self.assertFalse(sut.is_available())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)

    @patch('paramiko.SSHClient', autospec=True)
    def test_is_available_connection_timeout(self, m):
        m.return_value.connect = Mock(side_effect=socket.timeout)
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
        sut = SshLocation.from_configuration_data(configuration_data)
        self.assertFalse(sut.is_available())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)

    def test_from_configuration_data(self):
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
        sut = SshLocation.from_configuration_data(configuration_data)
        self.assertEquals(sut.path, path)
        self.assertEquals(sut.user, user)
        self.assertEquals(sut.host, host)
        self.assertEquals(sut.port, port)

    def test_from_configuration_data_with_default_port(self):
        user = 'bart'
        host = 'example.com'
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'host': host,
            'path': path,
        }
        sut = SshLocation.from_configuration_data(configuration_data)
        self.assertEquals(sut.port, 22)

    def test_from_configuration_data_without_user(self):
        host = 'example.com'
        port = 666
        path = '/var/cache'
        configuration_data = {
            'host': host,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_configuration_data(configuration_data)

    def test_from_configuration_data_without_host(self):
        user = 'bart'
        port = 666
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_configuration_data(configuration_data)

    def test_from_configuration_data_without_path(self):
        user = 'bart'
        host = 'example.com'
        port = 666
        configuration_data = {
            'user': user,
            'host': host,
            'port': port,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_configuration_data(configuration_data)

    def test_from_configuration_data_with_invalid_port_too_low(self):
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
            SshLocation.from_configuration_data(configuration_data)

    def test_from_configuration_data_with_invalid_port_too_high(self):
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
            SshLocation.from_configuration_data(configuration_data)


class FirstAvailableLocationTest(TestCase):
    def test_is_available(self):
        location_1 = PathLocation('/tmp/SomeNoneExistentPath')
        location_2 = PathLocation('/tmp')
        location_3 = PathLocation('/tmp')
        sut = FirstAvailableLocation([location_1, location_2, location_3])
        self.assertTrue(sut.is_available())

    def test_is_available_unavailable(self):
        location_1 = PathLocation('/tmp/SomeNoneExistentPath')
        location_2 = PathLocation('/tmp/SomeNoneExistentPath')
        location_3 = PathLocation('/tmp/SomeNoneExistentPath')
        sut = FirstAvailableLocation([location_1, location_2, location_3])
        self.assertFalse(sut.is_available())
