from unittest import TestCase

from backuppy.runner import Runner

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from backuppy.config import PluginConfiguration, Configuration
from backuppy.tests import CONFIGURATION_PATH


class RunnerTest(TestCase):
    def test_backup(self):
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        source = Mock(PluginConfiguration)
        target = Mock(PluginConfiguration)
        configuration = Configuration(configuration_file_path, source, [target])
        sut = Runner(configuration)
        sut.backup()
