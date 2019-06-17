import os
import subprocess
import time
from unittest import TestCase

from parameterized import parameterized

from backuppy.location import PathSource, PathTarget
from backuppy.task import backup, restore
from backuppy.tests import assert_paths_identical, build_files_stage_1, build_files_stage_2

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory

from backuppy.config import Configuration
from backuppy.notifier import Notifier


class BackupTest(TestCase):
    def test_backup_all(self):
        # Create the source directory.
        with TemporaryDirectory() as source_path:
            build_files_stage_1(source_path)

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
                assert_paths_identical(self, source_path, os.path.join(
                    target_path, 'latest'))
                real_snapshot_1_path = subprocess.check_output(['readlink', '-f', 'latest'], cwd=target_path).decode(
                    'utf-8').strip()

                # Sleep for two seconds, so we are (hopefully) absolutely sure the time-based snapshot name generator
                # will not generate identical names for all snapshots.
                time.sleep(2)

                result = backup(configuration)
                self.assertTrue(result)
                assert_paths_identical(self, os.path.join(
                    target_path, 'latest'), source_path)
                real_snapshot_2_path = subprocess.check_output(['readlink', '-f', 'latest'], cwd=target_path).decode(
                    'utf-8').strip()

                # Ensure the previous snapshot has not changed.
                assert_paths_identical(self, real_snapshot_1_path, source_path)

                # Sleep for two seconds, so we are (hopefully) absolutely sure the time-based snapshot name generator
                # will not generate identical names for all snapshots.
                time.sleep(2)

                # Change the source data and create another snapshot. Confirm the first two snapshots remain untouched,
                # and only the new one contains the changes.
                build_files_stage_2(source_path)
                result = backup(configuration)
                self.assertTrue(result)
                assert_paths_identical(self, os.path.join(
                    target_path, 'latest'), source_path)
                # Ensure the changes made to the source did not affect the previous snapshots.
                with self.assertRaises(AssertionError):
                    assert_paths_identical(
                        self, real_snapshot_1_path, source_path)
                with self.assertRaises(AssertionError):
                    assert_paths_identical(
                        self, real_snapshot_2_path, source_path)

    @parameterized.expand([
        ('sub',),
        ('sub/',),
    ])
    def test_backup_with_directory_path(self, path):
        # Create the source directory.
        with TemporaryDirectory() as source_path:
            build_files_stage_1(source_path)

            # Create the target directory.
            with TemporaryDirectory() as target_path:
                configuration = Configuration('Foo', verbose=True)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path + '/')
                configuration.target = PathTarget(
                    configuration.logger, configuration.notifier, target_path)

                # Back up the first time.
                result = backup(configuration, path)
                self.assertTrue(result)
                real_snapshot_1_path = subprocess.check_output(['readlink', '-f', 'latest'], cwd=target_path).decode(
                    'utf-8').strip()
                with self.assertRaises(AssertionError):
                    assert_paths_identical(
                        self, source_path, real_snapshot_1_path)
                assert_paths_identical(self, os.path.join(source_path, path),
                                       os.path.join(real_snapshot_1_path, path))

                # Sleep for two seconds, so we are (hopefully) absolutely sure the time-based snapshot name generator
                # will not generate identical names for all snapshots.
                time.sleep(2)

                result = backup(configuration, path)
                self.assertTrue(result)
                real_snapshot_2_path = subprocess.check_output(['readlink', '-f', 'latest'], cwd=target_path).decode(
                    'utf-8').strip()
                with self.assertRaises(AssertionError):
                    assert_paths_identical(
                        self, source_path, real_snapshot_2_path)
                assert_paths_identical(self, os.path.join(source_path, path),
                                       os.path.join(real_snapshot_2_path, path))

                # Ensure the previous snapshot has not changed.
                assert_paths_identical(self, os.path.join(real_snapshot_1_path, path), os.path.join(source_path, path))

    def test_backup_with_file_path(self):
        path = 'sub/some.file.in.subdirectory'
        # Create the source directory.
        with TemporaryDirectory() as source_path:
            build_files_stage_1(source_path)

            # Create the target directory.
            with TemporaryDirectory() as target_path:
                configuration = Configuration('Foo', verbose=True)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path + '/')
                configuration.target = PathTarget(
                    configuration.logger, configuration.notifier, target_path)

                # Back up the first time.
                result = backup(configuration, path)
                self.assertTrue(result)
                real_snapshot_1_path = subprocess.check_output(['readlink', '-f', 'latest'], cwd=target_path).decode(
                    'utf-8').strip()
                with self.assertRaises(AssertionError):
                    assert_paths_identical(
                        self, source_path, real_snapshot_1_path)
                assert_paths_identical(self, os.path.join(source_path, path),
                                       os.path.join(real_snapshot_1_path, path))

                # Sleep for two seconds, so we are (hopefully) absolutely sure the time-based snapshot name generator
                # will not generate identical names for all snapshots.
                time.sleep(2)

                result = backup(configuration, path)
                self.assertTrue(result)
                real_snapshot_2_path = subprocess.check_output(['readlink', '-f', 'latest'], cwd=target_path).decode(
                    'utf-8').strip()
                with self.assertRaises(AssertionError):
                    assert_paths_identical(
                        self, source_path, real_snapshot_2_path)
                assert_paths_identical(self, os.path.join(source_path, path),
                                       os.path.join(real_snapshot_2_path, path))

                # Ensure the previous snapshot has not changed.
                with self.assertRaises(AssertionError):
                    assert_paths_identical(
                        self, source_path, real_snapshot_1_path)
                assert_paths_identical(self, os.path.join(real_snapshot_1_path, path), os.path.join(source_path, path))

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

    @patch('backuppy.task.rsync')
    def test_backup_with_subprocess_error(self, m):
        m.side_effect = subprocess.CalledProcessError(7, '')
        # Create the source directory.
        with TemporaryDirectory() as source_path:
            # Create the target directory.
            with TemporaryDirectory() as target_path:
                configuration = Configuration('Foo', verbose=True)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path + '/')
                configuration.target = PathTarget(
                    configuration.logger, configuration.notifier, target_path)

                result = backup(configuration)
                self.assertFalse(result)

    def test_backup_with_exclude_include(self):
        exclude = ['./excluded', './contents.excluded/*']
        include = ['./contents.excluded/some.explicitly.included.file.in.explicitly.contents.excluded.subdirectory']
        # Create the source directory.
        with TemporaryDirectory() as source_path:
            with open(os.path.join(source_path, 'some.implicitly.included.file'), mode='w+t') as f:
                f.write('This is just some implicitly included file...')
                f.flush()
            os.makedirs(os.path.join(source_path, 'excluded'))
            with open(os.path.join(source_path, 'excluded', 'some.implicitly.excluded.file.in.explicitly.excluded.subdirectory'), mode='w+t') as f:
                f.write('This is just some implicitly excluded file in an explicitly excluded subdirectory...')
                f.flush()
            os.makedirs(os.path.join(source_path, 'included'))
            with open(os.path.join(source_path, 'included', 'some.implicitly.included.file.in.implicitly.included.subdirectory'), mode='w+t') as f:
                f.write('This is just some implicitly excluded file in an explicitly excluded subdirectory...')
                f.flush()
            os.makedirs(os.path.join(source_path, 'contents.excluded'))
            with open(os.path.join(source_path, 'contents.excluded', 'some.implicitly.excluded.file.in.explicitly.contents.excluded.subdirectory'), mode='w+t') as f:
                f.write('This is just some implicitly excluded file in an explicitly contents-excluded subdirectory...')
                f.flush()
            with open(os.path.join(source_path, 'contents.excluded', 'some.explicitly.included.file.in.explicitly.contents.excluded.subdirectory'), mode='w+t') as f:
                f.write('This is just some explicitly included file in an explicitly contents-excluded subdirectory...')
                f.flush()

            # Create the target directory.
            with TemporaryDirectory() as target_path:
                configuration = Configuration('Foo', exclude=exclude, include=include)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path + '/')
                configuration.target = PathTarget(
                    configuration.logger, configuration.notifier, target_path)

                # Back up the first time.
                result = backup(configuration)
                self.assertTrue(result)
                with self.assertRaises(AssertionError):
                    assert_paths_identical(self, source_path, os.path.join(target_path, 'latest'))


class RestoreTest(TestCase):
    def test_restore_all(self):
        # Create the target directory.
        with TemporaryDirectory() as target_path:
            latest_path = os.path.join(target_path, 'latest')
            os.makedirs(latest_path)
            build_files_stage_1(latest_path)

            # Create the source directory.
            with TemporaryDirectory() as source_path:
                configuration = Configuration('Foo', verbose=True)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path + '/')
                configuration.target = PathTarget(
                    configuration.logger, configuration.notifier, target_path)

                result = restore(configuration)
                self.assertTrue(result)
                subprocess.check_call(['ls', '-la', source_path])
                assert_paths_identical(self, source_path, os.path.join(
                    target_path, 'latest'))

    @parameterized.expand([
        ('sub/',),
        ('/sub/',),
    ])
    def test_restore_with_directory_path(self, path):
        # Create the target directory.
        with TemporaryDirectory() as target_path:
            latest_path = os.path.join(target_path, 'latest')
            os.makedirs(latest_path)
            build_files_stage_1(latest_path)

            # Create the source directory.
            with TemporaryDirectory() as source_path:
                configuration = Configuration('Foo', verbose=True)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path + '/')
                configuration.target = PathTarget(
                    configuration.logger, configuration.notifier, target_path)

                result = restore(configuration, path)
                self.assertTrue(result)
                with self.assertRaises(AssertionError):
                    assert_paths_identical(self, source_path, os.path.join(
                        target_path, 'latest'))
                assert_paths_identical(self, os.path.join(source_path, path),
                                       os.path.join(target_path, 'latest', path))

    @parameterized.expand([
        ('sub/some.file.in.subdirectory',),
        ('/sub/some.file.in.subdirectory',),
    ])
    def test_restore_with_file_path(self, path):
        # Create the target directory.
        with TemporaryDirectory() as target_path:
            latest_path = os.path.join(target_path, 'latest')
            os.makedirs(latest_path)
            build_files_stage_1(latest_path)

            # Create the source directory.
            with TemporaryDirectory() as source_path:
                configuration = Configuration('Foo', verbose=True)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path + '/')
                configuration.target = PathTarget(
                    configuration.logger, configuration.notifier, target_path)

                result = restore(configuration, path)
                self.assertTrue(result)
                with self.assertRaises(AssertionError):
                    assert_paths_identical(self, source_path, os.path.join(
                        target_path, 'latest'))
                assert_paths_identical(self, os.path.join(source_path, path),
                                       os.path.join(target_path, 'latest', path))

    def test_restore_with_unavailable_source(self):
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
                result = restore(configuration)
                self.assertFalse(result)

    def test_restore_with_unavailable_target(self):
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
                result = restore(configuration)
                self.assertFalse(result)

    @patch('backuppy.task.rsync')
    def test_restore_with_subprocess_error(self, m):
        m.side_effect = subprocess.CalledProcessError(7, '')
        # Create the target directory.
        with TemporaryDirectory() as target_path:
            # Create the source directory.
            with TemporaryDirectory() as source_path:
                configuration = Configuration('Foo', verbose=True)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path + '/')
                configuration.target = PathTarget(
                    configuration.logger, configuration.notifier, target_path)

                result = restore(configuration)
                self.assertFalse(result)
