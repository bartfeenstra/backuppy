from unittest import TestCase

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
from backuppy.location import PathLocation
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
                    notifier = Mock(Notifier)
                    source = PathLocation(notifier, source_path + '/')
                    target = PathLocation(notifier, target_path)
                    configuration = Mock(Configuration)
                    result = backup(configuration, notifier, source, target)
                    self.assertTrue(result)

                    # Assert source and target content are identical.
                    with open('%s/%s' % (target_path, file_name)) as f:
                        self.assertEquals(f.read(), file_contents)

    def test_backup_with_unavailable_source(self):
        # Create the source directory.
        with TemporaryDirectory() as source_path:
            # Create the target directory.
            with TemporaryDirectory() as target_path:
                notifier = Mock(Notifier)
                source = PathLocation(notifier, source_path + '/NonExistentPath')
                target = PathLocation(notifier, target_path)
                configuration = Mock(Configuration)
                result = backup(configuration, notifier, source, target)
                self.assertFalse(result)

    def test_backup_with_unavailable_target(self):
        # Create the source directory.
        with TemporaryDirectory() as source_path:
            # Create the target directory.
            with TemporaryDirectory() as target_path:
                notifier = Mock(Notifier)
                source = PathLocation(notifier, source_path)
                target = PathLocation(notifier, target_path + '/NonExistentPath')
                configuration = Mock(Configuration)
                result = backup(configuration, notifier, source, target)
                self.assertFalse(result)
