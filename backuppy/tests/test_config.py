from unittest import TestCase

from backuppy.tests import CONFIGURATION_PATH

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from backuppy.config import from_json, Configuration, PluginConfiguration


class ConfigurationTest(TestCase):
    def test_verbose(self):
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        source = Mock(PluginConfiguration)
        target = Mock(PluginConfiguration)
        sut = Configuration(configuration_file_path, source, [target], verbose=True)
        self.assertTrue(sut.verbose)
        sut.verbose = False
        self.assertFalse(sut.verbose)

    def test_working_directory(self):
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        source = Mock(PluginConfiguration)
        target = Mock(PluginConfiguration)
        sut = Configuration(configuration_file_path, source, [target])
        self.assertEquals(sut.working_directory, CONFIGURATION_PATH)

    def test_name_with_name(self):
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        source = Mock(PluginConfiguration)
        target = Mock(PluginConfiguration)
        name = 'Coffee and apple pie'
        sut = Configuration(configuration_file_path, source, [target], name)
        self.assertEquals(sut.name, name)

    def test_name_without_name(self):
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        source = Mock(PluginConfiguration)
        target = Mock(PluginConfiguration)
        sut = Configuration(configuration_file_path, source, [target])
        self.assertEquals(sut.name, CONFIGURATION_PATH)

    def test_notifiers(self):
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        source = Mock(PluginConfiguration)
        target = Mock(PluginConfiguration)
        notifiers = [Mock(PluginConfiguration), Mock(PluginConfiguration)]
        sut = Configuration(configuration_file_path, source, [target], notifiers=notifiers)
        self.assertEquals(sut.notifiers, notifiers)


class FromJsonTest(TestCase):
    def test_from_json(self):
        with open('%s/backuppy.json' % CONFIGURATION_PATH) as f:
            configuration = from_json(f)
        self.assertTrue(configuration.verbose)
