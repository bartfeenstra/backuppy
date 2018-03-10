import os
import socket
import subprocess
from unittest import TestCase

from paramiko import SSHException

from backuppy.location import PathLocation, SshTarget, FirstAvailableTarget, _new_snapshot_args, PathTarget
from backuppy.notifier import Notifier

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory


class NewSnapshotArgsTest(TestCase):
    def test_new_snapshot_args(self):
        snapshot_name = 'foo_bar'
        with TemporaryDirectory() as path:
            for args in _new_snapshot_args(snapshot_name):
                subprocess.call(args, cwd=path)
            self.assertTrue(os.path.exists('/'.join([path, snapshot_name])))
            self.assertTrue(os.path.exists('/'.join([path, 'latest'])))


class PathLocationTest(TestCase):
    class PathLocation(PathLocation):
        def snapshot(self):
            pass

        def to_rsync(self):
            pass

    def test_is_available(self):
        notifier = Mock(Notifier)
        path = '/tmp'
        sut = self.PathLocation(notifier, path)
        self.assertTrue(sut.is_available())

    def test_is_available_unavailable(self):
        notifier = Mock(Notifier)
        path = '/tmp/SomeNoneExistentPath'
        sut = self.PathLocation(notifier, path)
        self.assertFalse(sut.is_available())


class PathTargetTest(TestCase):
    def test_snapshot(self):
        notifier = Mock(Notifier)
        with TemporaryDirectory() as path:
            sut = PathTarget(notifier, path)
            sut.snapshot()
            self.assertTrue(os.path.exists('/'.join([path, 'latest'])))


class SshTargetTest(TestCase):
    @patch('paramiko.SSHClient', autospec=True)
    def test_is_available(self, m):
        notifier = Mock(Notifier)
        user = 'bart'
        host = 'example.com'
        port = 666
        path = '/var/cache'
        sut = SshTarget(notifier, user, host, path, port)
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
        sut = SshTarget(notifier, user, host, path, port)
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
        sut = SshTarget(notifier, user, host, path, port)
        self.assertFalse(sut.is_available())
        self.assertNotEquals([], m.return_value.connect.mock_calls)
        m.return_value.connect.assert_called_with(host, port, user, timeout=9)


class FirstAvailableTargetTest(TestCase):
    def test_is_available(self):
        notifier = Mock(Notifier)
        location_1 = PathTarget(notifier, '/tmp/SomeNoneExistentPath')
        location_2 = PathTarget(notifier, '/tmp')
        location_3 = PathTarget(notifier, '/tmp')
        sut = FirstAvailableTarget([location_1, location_2, location_3])
        self.assertTrue(sut.is_available())
        # Try again, so we cover the SUT's internal static cache.
        self.assertTrue(sut.is_available())

    def test_is_available_unavailable(self):
        notifier = Mock(Notifier)
        location_1 = PathTarget(notifier, '/tmp/SomeNoneExistentPath')
        location_2 = PathTarget(notifier, '/tmp/SomeNoneExistentPath')
        location_3 = PathTarget(notifier, '/tmp/SomeNoneExistentPath')
        sut = FirstAvailableTarget([location_1, location_2, location_3])
        self.assertFalse(sut.is_available())
        # Try again, so we cover the SUT's internal static cache.
        self.assertFalse(sut.is_available())
