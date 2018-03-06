from unittest import TestCase

from backuppy.task import backup

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from backuppy.config import Configuration
from backuppy.location import PathLocation
from backuppy.notifier import Notifier


class BackupTest(TestCase):
    def test_backup(self):
        notifier = Mock(Notifier)
        source = PathLocation(notifier, '/tmp')
        target = PathLocation(notifier, '/tmp')
        configuration = Mock(Configuration)
        backup(configuration, notifier, source, target)
