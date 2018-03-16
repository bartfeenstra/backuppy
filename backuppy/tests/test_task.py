import os
import subprocess
import time
from unittest import TestCase

from backuppy import assert_path
from backuppy.location import PathSource, PathTarget
from backuppy.task import backup

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

from backuppy.config import Configuration
from backuppy.notifier import Notifier


class BackupTest(TestCase):
    def test_backup(self):
        file_name = 'some.file'
        file_contents = 'This is just some file...'
        sub_file_name = 'some.file.in.subdirectory'
        sub_file_contents = 'This is just some other file in a subdirectory...'

        # Create the source directory.
        with TemporaryDirectory() as source_path:
            # Create source content.
            with open(os.path.join(source_path, file_name), mode='w+t') as f:
                f.write(file_contents)
                f.flush()
            os.makedirs(os.path.join(source_path, 'sub'))
            with open(os.path.join(source_path, sub_file_name), mode='w+t') as f:
                f.write(sub_file_contents)
                f.flush()

            # Create the target directory.
            with TemporaryDirectory() as target_path:
                configuration = Configuration('Foo', verbose=True)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path + '/')
                configuration.target = PathTarget(
                    configuration.logger, configuration.notifier, target_path)

                # Back up the first time.
                result = backup(configuration)
                self.assertTrue(result)
                assert_path(self, source_path, target_path + '/latest')
                real_snapshot_1_path = subprocess.check_output(['readlink', '-f', 'latest'], cwd=target_path).decode(
                    'utf-8').strip()

                # Sleep for two seconds, so we are (hopefully) absolutely sure the time-based snapshot name generator
                # will not generate identical names for all snapshots.
                time.sleep(2)

                result = backup(configuration)
                self.assertTrue(result)
                assert_path(self, source_path, target_path + '/latest')
                real_snapshot_2_path = subprocess.check_output(['readlink', '-f', 'latest'], cwd=target_path).decode(
                    'utf-8').strip()

                # Ensure both snapshots, made from the same source data, are equal.
                assert_path(self, real_snapshot_1_path, real_snapshot_2_path)

                # Sleep for two seconds, so we are (hopefully) absolutely sure the time-based snapshot name generator
                # will not generate identical names for all snapshots.
                time.sleep(2)

                # Change the source data and create another snapshot. Confirm the first two snapshots remain untouched,\
                # and only the new one contains the changes.
                later_file_name = 'some.later.file'
                later_file_contents = 'These contents were added much later.'
                with open(os.path.join(source_path, later_file_name), mode='w+t') as f:
                    f.write(later_file_contents)
                    f.flush()
                result = backup(configuration)
                self.assertTrue(result)
                assert_path(self, source_path, target_path + '/latest')
                assert_path(self, real_snapshot_1_path, real_snapshot_2_path)
                with self.assertRaises(AssertionError):
                    assert_path(self, source_path, real_snapshot_1_path)
                with self.assertRaises(AssertionError):
                    assert_path(self, source_path, real_snapshot_2_path)

    def test_backup_with_unavailable_source(self):
        # Create the source directory.
        with TemporaryDirectory() as source_path:
            # Create the target directory.
            with TemporaryDirectory() as target_path:
                configuration = Configuration('Foo', verbose=True)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path + '/NonExistentPath')
                configuration.target = PathTarget(
                    configuration.logger, configuration.notifier, target_path)
                result = backup(configuration)
                self.assertFalse(result)

    def test_backup_with_unavailable_target(self):
        # Create the source directory.
        with TemporaryDirectory() as source_path:
            # Create the target directory.
            with TemporaryDirectory() as target_path:
                configuration = Configuration('Foo', verbose=True)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path)
                configuration.target = PathTarget(
                    configuration.logger, configuration.notifier, target_path + '/NonExistentPath')
                result = backup(configuration)
                self.assertFalse(result)
