from unittest import TestCase

try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock

from backuppy.config import Configuration
from backuppy.plugin import new_source, new_notifier, new_target


class NewSourceTest(TestCase):
    def test_new_source_of_unknown_type(self):
        with self.assertRaises(ValueError):
            configuration = Mock(Configuration)
            new_source(configuration, 'NonExistentType')


class NewTargetTest(TestCase):
    def test_new_target_of_unknown_type(self):
        with self.assertRaises(ValueError):
            configuration = Mock(Configuration)
            new_target(configuration, 'NonExistentType')


class NewNotifierTest(TestCase):
    def test_new_notifier_of_unknown_type(self):
        with self.assertRaises(ValueError):
            configuration = Mock(Configuration)
            new_notifier(configuration, 'NonExistentType')
