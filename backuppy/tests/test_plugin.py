from unittest import TestCase

from backuppy.notifier import Notifier

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from backuppy.config import Configuration
from backuppy.plugin import new_source, new_notifier, new_target


class NewSourceTest(TestCase):
    def test_new_source_of_unknown_type(self):
        with self.assertRaises(ValueError):
            configuration = Mock(Configuration)
            new_source(configuration, 'NonExistentType')


class NewTargetTest(TestCase):
    def test_new_target_of_unknown_type(self):
        with self.assertRaises(ValueError):
            configuration = Mock(Configuration)
            new_target(configuration, 'NonExistentType')


class NewNotifierTest(TestCase):
    def test_new_notifier_of_unknown_type(self):
        with self.assertRaises(ValueError):
            configuration = Mock(Configuration)
            new_notifier(configuration, 'NonExistentType')


class NewPathSourceTest(TestCase):
    def test_new_source(self):
        configuration = Configuration('Foo', working_directory='/')
        configuration.notifier = Mock(Notifier)
        path = '/var/cache'
        configuration_data = {
            'path': path,
        }
        source = new_source(configuration, 'path', configuration_data)
        self.assertEquals(source.path, path)

    def test_new_source_without_path(self):
        configuration = Configuration('Foo', working_directory='/')
        configuration.notifier = Mock(Notifier)
        configuration_data = {}
        with self.assertRaises(ValueError):
            new_source(configuration, 'path', configuration_data)


class NewPathTargetTest(TestCase):
    def test_new_target(self):
        configuration = Configuration('Foo', working_directory='/')
        configuration.notifier = Mock(Notifier)
        path = '/var/cache'
        configuration_data = {
            'path': path,
        }
        target = new_target(configuration, 'path', configuration_data)
        self.assertEquals(target.path, path)

    def test_new_target_without_path(self):
        configuration = Configuration('Foo', working_directory='/')
        configuration.notifier = Mock(Notifier)
        configuration_data = {}
        with self.assertRaises(ValueError):
            new_target(configuration, 'path', configuration_data)


class NewSshTargetTest(TestCase):
    def test_new_target(self):
        configuration = Configuration('Foo')
        configuration.notifier = Mock(Notifier)
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
        target = new_target(configuration, 'ssh', configuration_data)
        self.assertEquals(target.path, path)
        self.assertEquals(target.user, user)
        self.assertEquals(target.host, host)
        self.assertEquals(target.port, port)

    def test_new_target_with_default_port(self):
        configuration = Configuration('Foo')
        configuration.notifier = Mock(Notifier)
        user = 'bart'
        host = 'example.com'
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'host': host,
            'path': path,
        }
        sut = new_target(configuration, 'ssh', configuration_data)
        self.assertEquals(sut.port, 22)

    def test_new_target_without_user(self):
        configuration = Configuration('Foo')
        configuration.notifier = Mock(Notifier)
        host = 'example.com'
        port = 666
        path = '/var/cache'
        configuration_data = {
            'host': host,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            new_target(configuration, 'ssh', configuration_data)

    def test_new_target_without_host(self):
        configuration = Configuration('Foo')
        configuration.notifier = Mock(Notifier)
        user = 'bart'
        port = 666
        path = '/var/cache'
        configuration_data = {
            'user': user,
            'port': port,
            'path': path,
        }
        with self.assertRaises(ValueError):
            new_target(configuration, 'ssh', configuration_data)

    def test_new_target_without_path(self):
        configuration = Configuration('Foo')
        configuration.notifier = Mock(Notifier)
        user = 'bart'
        host = 'example.com'
        port = 666
        configuration_data = {
            'user': user,
            'host': host,
            'port': port,
        }
        with self.assertRaises(ValueError):
            new_target(configuration, 'ssh', configuration_data)

    def test_new_target_with_invalid_port_too_low(self):
        configuration = Configuration('Foo')
        configuration.notifier = Mock(Notifier)
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
            new_target(configuration, 'ssh', configuration_data)

    def test_new_target_with_invalid_port_too_high(self):
        configuration = Configuration('Foo')
        configuration.notifier = Mock(Notifier)
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
            new_target(configuration, 'ssh', configuration_data)
