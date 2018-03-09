from unittest import TestCase

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

        # Create the source directory.
        with TemporaryDirectory() as source_path:
            # Create source content.
            with open('%s/%s' % (source_path, file_name), mode='w+t') as f:
                f.write(file_contents)
                f.flush()

                # Create the target directory.
                with TemporaryDirectory() as target_path:
                    configuration = Configuration('Foo')
                    configuration.notifier = Mock(Notifier)
                    configuration.source = PathSource(configuration.notifier, source_path + '/')
                    configuration.target = PathTarget(configuration.notifier, target_path)
                    result = backup(configuration)
                    self.assertTrue(result)

                    # Assert source and target content are identical.
                    with open('%s/latest/%s' % (target_path, file_name), ) as f:
                        self.assertEquals(f.read(), file_contents)

    def test_backup_with_unavailable_source(self):
        # Create the source directory.
        with TemporaryDirectory() as source_path:
            # Create the target directory.
            with TemporaryDirectory() as target_path:
                configuration = Configuration('Foo')
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(configuration.notifier, source_path + '/NonExistentPath')
                configuration.target = PathTarget(configuration.notifier, target_path)
                result = backup(configuration)
                self.assertFalse(result)

    def test_backup_with_unavailable_target(self):
        # Create the source directory.
        with TemporaryDirectory() as source_path:
            # Create the target directory.
            with TemporaryDirectory() as target_path:
                configuration = Configuration('Foo')
                configuration.notifier = Mock(Notifier)
                configuration.source = PathSource(configuration.notifier, source_path)
                configuration.target = PathTarget(configuration.notifier, target_path + '/NonExistentPath')
                result = backup(configuration)
                self.assertFalse(result)
