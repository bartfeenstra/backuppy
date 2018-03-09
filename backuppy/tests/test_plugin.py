from unittest import TestCase

from backuppy.notifier import Notifier

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from backuppy.config import PluginConfiguration, Configuration
from backuppy.plugin import new_source, new_notifier, new_target


class NewSourceTest(TestCase):
    def test_new_source_of_unknown_type(self):
        source_configuration = PluginConfiguration('NonExistentType')
        with self.assertRaises(ValueError):
            configuration = Mock(Configuration)
            notifier = Mock(Notifier)
            new_source(configuration, notifier, source_configuration)


class NewTargetTest(TestCase):
    def test_new_target_of_unknown_type(self):
        target_configuration = PluginConfiguration('NonExistentType')
        with self.assertRaises(ValueError):
            configuration = Mock(Configuration)
            notifier = Mock(Notifier)
            new_target(configuration, notifier, target_configuration)


class NewNotifierTest(TestCase):
    def test_new_notifier_of_unknown_type(self):
        notifier_configuration = PluginConfiguration('NonExistentType')
        with self.assertRaises(ValueError):
            configuration = Mock(Configuration)
            notifier = Mock(Notifier)
            new_notifier(configuration, notifier, notifier_configuration)
