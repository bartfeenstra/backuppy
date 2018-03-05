from unittest import TestCase

from backuppy.location import PathLocation, SshLocation


class PathLocationTest(TestCase):
    def test_is_ready(self):
        path = '/var/cache'
        sut = PathLocation(path)
        self.assertTrue(sut.is_ready())

    def test_from_raw(self):
        configuration_file_path = '/'
        path = '/var/cache'
        data = {
            'path': path,
        }
        sut = PathLocation.from_raw(configuration_file_path, data)
        self.assertEquals(sut.path, path)

    def test_from_raw_without_path(self):
        configuration_file_path = '/'
        data = {}
        with self.assertRaises(ValueError):
            PathLocation.from_raw(configuration_file_path, data)


class SshLocationTest(TestCase):
    def test_from_raw(self):
        configuration_file_path = '/'
        user = 'bart'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        data = {
            'user': user,
            'host': host,
            'port': port,
            'path': path,
        }
        sut = SshLocation.from_raw(configuration_file_path, data)
        self.assertEquals(sut.path, path)
        self.assertEquals(sut.user, user)
        self.assertEquals(sut.host, host)
        self.assertEquals(sut.port, port)

    def test_from_raw_with_default_port(self):
        configuration_file_path = '/'
        user = 'bart'
        host = 'example.com'
        path = '/var/cache'
        data = {
            'user': user,
            'host': host,
            'path': path,
        }
        sut = SshLocation.from_raw(configuration_file_path, data)
        self.assertEquals(sut.port, 22)

    def test_from_raw_without_user(self):
        configuration_file_path = '/'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        data = {
            'host': host,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_raw(configuration_file_path, data)

    def test_from_raw_without_host(self):
        configuration_file_path = '/'
        user = 'bart'
        port = 666
        path = '/var/cache'
        data = {
            'user': user,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_raw(configuration_file_path, data)

    def test_from_raw_without_path(self):
        configuration_file_path = '/'
        user = 'bart'
        host = 'example.com'
        port = 666
        data = {
            'user': user,
            'host': host,
            'port': port,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_raw(configuration_file_path, data)

    def test_from_raw_with_invalid_port_too_low(self):
        configuration_file_path = '/'
        user = 'bart'
        host = 'example.com'
        port = -1
        path = '/var/cache'
        data = {
            'user': user,
            'host': host,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_raw(configuration_file_path, data)

    def test_from_raw_with_invalid_port_too_high(self):
        configuration_file_path = '/'
        user = 'bart'
        host = 'example.com'
        port = 65536
        path = '/var/cache'
        data = {
            'user': user,
            'host': host,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            SshLocation.from_raw(configuration_file_path, data)
