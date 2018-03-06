import socket
from unittest import TestCase

from paramiko import SSHException

from backuppy.location import PathLocation, SshLocation, FirstAvailableLocation
from backuppy.notifier import Notifier

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch


class PathLocationTest(TestCase):
    def test_is_available(self):
        notifier = Mock(Notifier)
        path = '/tmp'
        sut = PathLocation(notifier, path)
        self.assertTrue(sut.is_available())

    def test_is_available_unavailable(self):
        notifier = Mock(Notifier)
        path = '/tmp/SomeNoneExistentPath'
        sut = PathLocation(notifier, path)
        self.assertFalse(sut.is_available())

    def test_from_configuration_data(self):
        notifier = Mock(Notifier)
        working_directory = '/'
        path = '/var/cache'
        configuration_data = {
            'path': path,
        }
        sut = PathLocation.from_configuration_data(notifier, working_directory, configuration_data)
        self.assertEquals(sut.path, path)

    def test_from_configuration_data_without_path(self):
        notifier = Mock(Notifier)
        working_directory = '/'
        configuration_data = {}
        with self.assertRaises(ValueError):
            PathLocation.from_configuration_data(notifier, working_directory, configuration_data)


class SshLocationTest(TestCase):
    @patch('paramiko.SSHClient', autospec=True)
    def test_is_available(self, m):
        notifier = Mock(Notifier)
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
        sut = SshLocation.from_configuration_data(notifier, configuration_data)
        self.assertTrue(sut.is_available())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)

    @patch('paramiko.SSHClient', autospec=True)
    def test_is_available_connection_error(self, m):
        m.return_value.connect = Mock(side_effect=SSHException)
        notifier = Mock(Notifier)
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
        sut = SshLocation.from_configuration_data(notifier, configuration_data)
        self.assertFalse(sut.is_available())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)

    @patch('paramiko.SSHClient', autospec=True)
    def test_is_available_connection_timeout(self, m):
        m.return_value.connect = Mock(side_effect=socket.timeout)
        notifier = Mock(Notifier)
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
        sut = SshLocation.from_configuration_data(notifier, configuration_data)
        self.assertFalse(sut.is_available())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)

    def test_from_configuration_data(self):
        notifier = Mock(Notifier)
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
        sut = SshLocation.from_configuration_data(notifier, configuration_data)
        self.assertEquals(sut.path, path)
        self.assertEquals(sut.user, user)
        self.assertEquals(sut.host, host)
        self.assertEquals(sut.port, port)

    def test_from_configuration_data_with_default_port(self):
        notifier = Mock(Notifier)
        user = 'bart'
        host = 'example.com'
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'host': host,
            'path': path,
        }
        sut = SshLocation.from_configuration_data(notifier, configuration_data)
        self.assertEquals(sut.port, 22)

    def test_from_configuration_data_without_user(self):
        notifier = Mock(Notifier)
        host = 'example.com'
        port = 666
        path = '/var/cache'
        configuration_data = {
            'host': host,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_configuration_data(notifier, configuration_data)

    def test_from_configuration_data_without_host(self):
        notifier = Mock(Notifier)
        user = 'bart'
        port = 666
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_configuration_data(notifier, configuration_data)

    def test_from_configuration_data_without_path(self):
        notifier = Mock(Notifier)
        user = 'bart'
        host = 'example.com'
        port = 666
        configuration_data = {
            'user': user,
            'host': host,
            'port': port,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_configuration_data(notifier, configuration_data)

    def test_from_configuration_data_with_invalid_port_too_low(self):
        notifier = Mock(Notifier)
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
            SshLocation.from_configuration_data(notifier, configuration_data)

    def test_from_configuration_data_with_invalid_port_too_high(self):
        notifier = Mock(Notifier)
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
            SshLocation.from_configuration_data(notifier, configuration_data)


class FirstAvailableLocationTest(TestCase):
    def test_is_available(self):
        notifier = Mock(Notifier)
        location_1 = PathLocation(notifier, '/tmp/SomeNoneExistentPath')
        location_2 = PathLocation(notifier, '/tmp')
        location_3 = PathLocation(notifier, '/tmp')
        sut = FirstAvailableLocation([location_1, location_2, location_3])
        self.assertTrue(sut.is_available())
        # Try again, so we cover the SUT's internal static cache.
        self.assertTrue(sut.is_available())

    def test_is_available_unavailable(self):
        notifier = Mock(Notifier)
        location_1 = PathLocation(notifier, '/tmp/SomeNoneExistentPath')
        location_2 = PathLocation(notifier, '/tmp/SomeNoneExistentPath')
        location_3 = PathLocation(notifier, '/tmp/SomeNoneExistentPath')
        sut = FirstAvailableLocation([location_1, location_2, location_3])
        self.assertFalse(sut.is_available())
        # Try again, so we cover the SUT's internal static cache.
        self.assertFalse(sut.is_available())
