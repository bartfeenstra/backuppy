from unittest import TestCase

from backuppy.notifier import Notifier

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from backuppy.config import PluginConfiguration, Configuration
from backuppy.discover import new_location


class NewLocationTest(TestCase):
    def test_new_location_of_unknown_type(self):
        location_configuration = PluginConfiguration('NonExistentType')
        with self.assertRaises(ValueError):
            configuration = Mock(Configuration)
            notifier = Mock(Notifier)
            new_location(configuration, notifier, location_configuration)


class NewNotifierTest(TestCase):
    def test_new_location_of_unknown_type(self):
        location_configuration = PluginConfiguration('NonExistentType')
        with self.assertRaises(ValueError):
            configuration = Mock(Configuration)
            notifier = Mock(Notifier)
            new_location(configuration, notifier, location_configuration)
