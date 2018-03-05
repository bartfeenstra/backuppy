from unittest import TestCase
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from backuppy.notifier import NotifySendNotifier, GroupedNotifiers


class GroupedNotifiersTest(TestCase):
    def test_notify(self):
        notifier_1 = Mock()
        notifier_2 = Mock()
        notifier_3 = Mock()
        sut = GroupedNotifiers([notifier_1, notifier_2, notifier_3])
        message = 'Something happened!'
        sut.notify(message)
        notifier_1.notify.assert_called_with(message)
        notifier_2.notify.assert_called_with(message)
        notifier_3.notify.assert_called_with(message)


class NotifySendNotifierTest(TestCase):
    @patch('subprocess.call')
    def test_notify(self, m):
        sut = NotifySendNotifier()
        message = 'Something happened!'
        sut.notify(message)
        m.assert_called_with(('notify-send', "'%s'" % message))
