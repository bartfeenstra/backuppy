from unittest import TestCase
try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from backuppy.notifier import NotifySendNotifier, GroupedNotifiers


class GroupedNotifiersTest(TestCase):
    def test_state(self):
        notifier_1 = Mock()
        notifier_2 = Mock()
        notifier_3 = Mock()
        sut = GroupedNotifiers([notifier_1, notifier_2, notifier_3])
        message = 'Something happened!'
        sut.state(message)
        notifier_1.state.assert_called_with(message)
        notifier_2.state.assert_called_with(message)
        notifier_3.state.assert_called_with(message)

    def test_inform(self):
        notifier_1 = Mock()
        notifier_2 = Mock()
        notifier_3 = Mock()
        sut = GroupedNotifiers([notifier_1, notifier_2, notifier_3])
        message = 'Something happened!'
        sut.inform(message)
        notifier_1.inform.assert_called_with(message)
        notifier_2.inform.assert_called_with(message)
        notifier_3.inform.assert_called_with(message)

    def test_confirm(self):
        notifier_1 = Mock()
        notifier_2 = Mock()
        notifier_3 = Mock()
        sut = GroupedNotifiers([notifier_1, notifier_2, notifier_3])
        message = 'Something happened!'
        sut.confirm(message)
        notifier_1.confirm.assert_called_with(message)
        notifier_2.confirm.assert_called_with(message)
        notifier_3.confirm.assert_called_with(message)

    def test_alert(self):
        notifier_1 = Mock()
        notifier_2 = Mock()
        notifier_3 = Mock()
        sut = GroupedNotifiers([notifier_1, notifier_2, notifier_3])
        message = 'Something happened!'
        sut.alert(message)
        notifier_1.alert.assert_called_with(message)
        notifier_2.alert.assert_called_with(message)
        notifier_3.alert.assert_called_with(message)


class NotifySendNotifierTest(TestCase):
    @patch('subprocess.call')
    def test_state(self, m):
        sut = NotifySendNotifier()
        message = 'Something happened!'
        sut.state(message)
        m.assert_called_with(('notify-send', '-c', 'backuppy', '-u', 'low', message))

    @patch('subprocess.call')
    def test_inform(self, m):
        sut = NotifySendNotifier()
        message = 'Something happened!'
        sut.inform(message)
        m.assert_called_with(('notify-send', '-c', 'backuppy', '-u', 'normal', message))

    @patch('subprocess.call')
    def test_confirm(self, m):
        sut = NotifySendNotifier()
        message = 'Something happened!'
        sut.confirm(message)
        m.assert_called_with(('notify-send', '-c', 'backuppy', '-u', 'normal', message))

    @patch('subprocess.call')
    def test_alert(self, m):
        sut = NotifySendNotifier()
        message = 'Something happened!'
        sut.alert(message)
        m.assert_called_with(('notify-send', '-c', 'backuppy', '-u', 'critical', message))
