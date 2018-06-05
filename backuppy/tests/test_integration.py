import os
from tempfile import TemporaryDirectory
from unittest import TestCase

from backuppy.config import Configuration
from backuppy.location import PathSource
from backuppy.notifier import Notifier
from backuppy.task import backup
from backuppy.tests import SshLocationContainer, assert_paths_identical, build_files_stage_1

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock


class BackupToSshTargetTest(TestCase):
    def tearDown(self):
        self._container.stop()

    def test_backup(self):
        with TemporaryDirectory() as source_path:
            with TemporaryDirectory() as mirrored_local_target_path:
                self._container = SshLocationContainer(
                    mount_point=mirrored_local_target_path)
                self._container.start()

                build_files_stage_1(source_path)

                configuration = Configuration('Foo', verbose=True)
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(
                    configuration.logger, configuration.notifier, source_path + '/')
                configuration.target = self._container.target(configuration)

                result = backup(configuration)
                self.assertTrue(result)
                assert_paths_identical(self, source_path, os.path.join(
                    mirrored_local_target_path, 'latest'))
