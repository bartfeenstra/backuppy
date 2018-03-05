from unittest import TestCase

from backuppy.config import PluginConfiguration, Configuration
from backuppy.runner import Runner
from backuppy.tests import CONFIGURATION_PATH


class RunnerTest(TestCase):
    def test_backup(self):
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        source = PluginConfiguration('path', {
            'path': '/tmp'
        })
        target = PluginConfiguration('path', {
            'path': '/tmp'
        })
        configuration = Configuration(configuration_file_path, source, [target])
        sut = Runner(configuration)
        sut.backup()
