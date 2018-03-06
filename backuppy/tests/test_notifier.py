from unittest import TestCase

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from backuppy.notifier import NotifySendNotifier, GroupedNotifiers, CommandNotifier


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


class CommandNotifierTest(TestCase):
    @patch('subprocess.call')
    def test_state(self, m):
        state_args = ['some', 'state']
        fallback_args = ['some', 'fallback']
        sut = CommandNotifier(state_args=state_args + ['{message}'], fallback_args=fallback_args + ['{message}'])
        message = 'Something happened!'
        sut.state(message)
        m.assert_called_with(state_args + [message])

    @patch('subprocess.call')
    def test_state_should_fall_back(self, m):
        fallback_args = ['some', 'fallback']
        sut = CommandNotifier(fallback_args=fallback_args + ['{message}'])
        message = 'Something happened!'
        sut.state(message)
        m.assert_called_with(fallback_args + [message])

    @patch('subprocess.call')
    def test_inform(self, m):
        inform_args = ['some', 'inform']
        fallback_args = ['some', 'fallback']
        sut = CommandNotifier(inform_args=inform_args + ['{message}'], fallback_args=fallback_args + ['{message}'])
        message = 'Something happened!'
        sut.inform(message)
        m.assert_called_with(inform_args + [message])

    @patch('subprocess.call')
    def test_inform_should_fall_back(self, m):
        fallback_args = ['some', 'fallback']
        sut = CommandNotifier(fallback_args=fallback_args + ['{message}'])
        message = 'Something happened!'
        sut.inform(message)
        m.assert_called_with(fallback_args + [message])

    @patch('subprocess.call')
    def test_confirm(self, m):
        confirm_args = ['some', 'confirm']
        fallback_args = ['some', 'fallback']
        sut = CommandNotifier(confirm_args=confirm_args + ['{message}'], fallback_args=fallback_args + ['{message}'])
        message = 'Something happened!'
        sut.confirm(message)
        m.assert_called_with(confirm_args + [message])

    @patch('subprocess.call')
    def test_confirm_should_fall_back(self, m):
        fallback_args = ['some', 'fallback']
        sut = CommandNotifier(fallback_args=fallback_args + ['{message}'])
        message = 'Something happened!'
        sut.confirm(message)
        m.assert_called_with(fallback_args + [message])

    @patch('subprocess.call')
    def test_alert(self, m):
        alert_args = ['some', 'alert']
        fallback_args = ['some', 'fallback']
        sut = CommandNotifier(alert_args=alert_args + ['{message}'], fallback_args=fallback_args + ['{message}'])
        message = 'Something happened!'
        sut.alert(message)
        m.assert_called_with(alert_args + [message])

    @patch('subprocess.call')
    def test_alert_should_fall_back(self, m):
        fallback_args = ['some', 'fallback']
        sut = CommandNotifier(fallback_args=fallback_args + ['{message}'])
        message = 'Something happened!'
        sut.alert(message)
        m.assert_called_with(fallback_args + [message])

    def test_init_without_state_and_fallback(self):
        inform_args = ['some', 'inform']
        confirm_args = ['some', 'confirm']
        alert_args = ['some', 'alert']
        with self.assertRaises(ValueError):
            CommandNotifier(inform_args=inform_args, confirm_args=confirm_args, alert_args=alert_args)

    def test_init_without_inform_and_fallback(self):
        state_args = ['some', 'state']
        confirm_args = ['some', 'confirm']
        alert_args = ['some', 'alert']
        with self.assertRaises(ValueError):
            CommandNotifier(state_args=state_args, confirm_args=confirm_args, alert_args=alert_args)

    def test_init_without_confirm_and_fallback(self):
        state_args = ['some', 'state']
        inform_args = ['some', 'inform']
        alert_args = ['some', 'alert']
        with self.assertRaises(ValueError):
            CommandNotifier(state_args=state_args, inform_args=inform_args, alert_args=alert_args)

    def test_init_without_alert_and_fallback(self):
        state_args = ['some', 'state']
        inform_args = ['some', 'inform']
        confirm_args = ['some', 'confirm']
        with self.assertRaises(ValueError):
            CommandNotifier(state_args=state_args, inform_args=inform_args, confirm_args=confirm_args)

    def test_from_configuration_data_without_state_and_fallback(self):
        data = {
            'inform': ['some', 'inform'],
            'confirm': ['some', 'confirm'],
            'alert': ['some', 'alert'],
        }
        with self.assertRaises(ValueError):
            CommandNotifier.from_configuration_data(data)

    def test_from_configuration_data_without_inform_and_fallback(self):
        data = {
            'state': ['some', 'state'],
            'confirm': ['some', 'confirm'],
            'alert': ['some', 'alert'],
        }
        with self.assertRaises(ValueError):
            CommandNotifier.from_configuration_data(data)

    def test_from_configuration_data_without_confirm_and_fallback(self):
        data = {
            'state': ['some', 'state'],
            'inform': ['some', 'inform'],
            'alert': ['some', 'alert'],
        }
        with self.assertRaises(ValueError):
            CommandNotifier.from_configuration_data(data)

    def test_from_configuration_data_without_alert_and_fallback(self):
        data = {
            'state': ['some', 'state'],
            'inform': ['some', 'inform'],
            'confirm': ['some', 'confirm'],
        }
        with self.assertRaises(ValueError):
            CommandNotifier.from_configuration_data(data)


class NotifySendNotifierTest(TestCase):
    @patch('subprocess.call')
    def test_state(self, m):
        sut = NotifySendNotifier()
        message = 'Something happened!'
        sut.state(message)
        m.assert_called_with(['notify-send', '-c', 'backuppy', '-u', 'low', message])

    @patch('subprocess.call')
    def test_inform(self, m):
        sut = NotifySendNotifier()
        message = 'Something happened!'
        sut.inform(message)
        m.assert_called_with(['notify-send', '-c', 'backuppy', '-u', 'normal', message])

    @patch('subprocess.call')
    def test_confirm(self, m):
        sut = NotifySendNotifier()
        message = 'Something happened!'
        sut.confirm(message)
        m.assert_called_with(['notify-send', '-c', 'backuppy', '-u', 'normal', message])

    @patch('subprocess.call')
    def test_alert(self, m):
        sut = NotifySendNotifier()
        message = 'Something happened!'
        sut.alert(message)
        m.assert_called_with(['notify-send', '-c', 'backuppy', '-u', 'critical', message])
