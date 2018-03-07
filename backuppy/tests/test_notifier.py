from tempfile import NamedTemporaryFile
from unittest import TestCase

from backuppy.config import Configuration, PluginConfiguration
from backuppy.discover import new_notifier

try:
    from unittest.mock import patch, Mock
except ImportError:
    from mock import patch, Mock

from backuppy.notifier import NotifySendNotifier, GroupedNotifiers, CommandNotifier, FileNotifier, Notifier, \
    StdioNotifier


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


class FileNotifierTest(TestCase):
    def test_state(self):
        with NamedTemporaryFile(mode='a+t') as state_file:
            with NamedTemporaryFile(mode='a+t') as fallback_file:
                sut = FileNotifier(state_file=state_file, fallback_file=fallback_file)
                message = 'Something happened!'
                sut.state(message)
                state_file.seek(0)
                fallback_file.seek(0)
                self.assertEquals(state_file.read(), message + '\n')
                self.assertEquals(fallback_file.read(), '')

    def test_state_should_fall_back(self):
        with NamedTemporaryFile(mode='a+t') as fallback_file:
            sut = FileNotifier(fallback_file=fallback_file)
            message = 'Something happened!'
            sut.state(message)
            fallback_file.seek(0)
            self.assertEquals(fallback_file.read(), message + '\n')

    def test_inform(self):
        with NamedTemporaryFile(mode='a+t') as inform_file:
            with NamedTemporaryFile(mode='a+t') as fallback_file:
                sut = FileNotifier(inform_file=inform_file, fallback_file=fallback_file)
                message = 'Something happened!'
                sut.inform(message)
                inform_file.seek(0)
                fallback_file.seek(0)
                self.assertEquals(inform_file.read(), message + '\n')
                self.assertEquals(fallback_file.read(), '')

    def test_inform_should_fall_back(self):
        with NamedTemporaryFile(mode='a+t') as fallback_file:
            sut = FileNotifier(fallback_file=fallback_file)
            message = 'Something happened!'
            sut.inform(message)
            fallback_file.seek(0)
            self.assertEquals(fallback_file.read(), message + '\n')

    def test_confirm(self):
        with NamedTemporaryFile(mode='a+t') as confirm_file:
            with NamedTemporaryFile(mode='a+t') as fallback_file:
                sut = FileNotifier(confirm_file=confirm_file, fallback_file=fallback_file)
                message = 'Something happened!'
                sut.confirm(message)
                confirm_file.seek(0)
                fallback_file.seek(0)
                self.assertEquals(confirm_file.read(), message + '\n')
                self.assertEquals(fallback_file.read(), '')

    def test_confirm_should_fall_back(self):
        with NamedTemporaryFile(mode='a+t') as fallback_file:
            sut = FileNotifier(fallback_file=fallback_file)
            message = 'Something happened!'
            sut.confirm(message)
            fallback_file.seek(0)
            self.assertEquals(fallback_file.read(), message + '\n')

    def test_alert(self):
        with NamedTemporaryFile(mode='a+t') as alert_file:
            with NamedTemporaryFile(mode='a+t') as fallback_file:
                sut = FileNotifier(alert_file=alert_file, fallback_file=fallback_file)
                message = 'Something happened!'
                sut.alert(message)
                alert_file.seek(0)
                fallback_file.seek(0)
                self.assertEquals(alert_file.read(), message + '\n')
                self.assertEquals(fallback_file.read(), '')

    def test_alert_should_fall_back(self):
        with NamedTemporaryFile(mode='a+t') as fallback_file:
            sut = FileNotifier(fallback_file=fallback_file)
            message = 'Something happened!'
            sut.alert(message)
            fallback_file.seek(0)
            self.assertEquals(fallback_file.read(), message + '\n')

    def test_init_without_state_and_fallback(self):
        with NamedTemporaryFile(mode='a+t') as inform_file:
            with NamedTemporaryFile(mode='a+t') as confirm_file:
                with NamedTemporaryFile(mode='a+t') as alert_file:
                    with self.assertRaises(ValueError):
                        FileNotifier(inform_file=inform_file, confirm_file=confirm_file, alert_file=alert_file)

    def test_init_without_inform_and_fallback(self):
        with NamedTemporaryFile(mode='a+t') as state_file:
            with NamedTemporaryFile(mode='a+t') as confirm_file:
                with NamedTemporaryFile(mode='a+t') as alert_file:
                    with self.assertRaises(ValueError):
                        FileNotifier(state_file=state_file, confirm_file=confirm_file, alert_file=alert_file)

    def test_init_without_confirm_and_fallback(self):
        with NamedTemporaryFile(mode='a+t') as state_file:
            with NamedTemporaryFile(mode='a+t') as inform_file:
                with NamedTemporaryFile(mode='a+t') as alert_file:
                    with self.assertRaises(ValueError):
                        FileNotifier(state_file=state_file, inform_file=inform_file, alert_file=alert_file)

    def test_init_without_alert_and_fallback(self):
        with NamedTemporaryFile(mode='a+t') as state_file:
            with NamedTemporaryFile(mode='a+t') as inform_file:
                with NamedTemporaryFile(mode='a+t') as confirm_file:
                    with self.assertRaises(ValueError):
                        FileNotifier(state_file=state_file, inform_file=inform_file, confirm_file=confirm_file)

    def test_new_notifier_without_state_and_fallback(self):
        with NamedTemporaryFile(mode='a+t') as inform_file:
            with NamedTemporaryFile(mode='a+t') as confirm_file:
                with NamedTemporaryFile(mode='a+t') as alert_file:
                    data = {
                        'inform': inform_file.name,
                        'confirm': confirm_file.name,
                        'alert': alert_file.name,
                    }
                configuration = Mock(Configuration)
                notifier = Mock(Notifier)
                with self.assertRaises(ValueError):
                    new_notifier(configuration, notifier, PluginConfiguration('file', data))

    def test_new_notifier_without_inform_and_fallback(self):
        with NamedTemporaryFile(mode='a+t') as state_file:
            with NamedTemporaryFile(mode='a+t') as confirm_file:
                with NamedTemporaryFile(mode='a+t') as alert_file:
                    data = {
                        'state': state_file.name,
                        'confirm': confirm_file.name,
                        'alert': alert_file.name,
                    }
                    configuration = Mock(Configuration)
                    notifier = Mock(Notifier)
                    with self.assertRaises(ValueError):
                        new_notifier(configuration, notifier, PluginConfiguration('file', data))

    def test_new_notifier_without_confirm_and_fallback(self):
        with NamedTemporaryFile(mode='a+t') as state_file:
            with NamedTemporaryFile(mode='a+t') as inform_file:
                with NamedTemporaryFile(mode='a+t') as alert_file:
                    data = {
                        'state': state_file.name,
                        'inform': inform_file.name,
                        'alert': alert_file.name,
                    }
                    configuration = Mock(Configuration)
                    notifier = Mock(Notifier)
                    with self.assertRaises(ValueError):
                        new_notifier(configuration, notifier, PluginConfiguration('file', data))

    def test_new_notifier_without_alert_and_fallback(self):
        with NamedTemporaryFile(mode='a+t') as state_file:
            with NamedTemporaryFile(mode='a+t') as inform_file:
                with NamedTemporaryFile(mode='a+t') as confirm_file:
                    data = {
                        'state': state_file.name,
                        'inform': inform_file.name,
                        'confirm': confirm_file.name,
                    }
                    configuration = Mock(Configuration)
                    notifier = Mock(Notifier)
                    with self.assertRaises(ValueError):
                        new_notifier(configuration, notifier, PluginConfiguration('file', data))


class StdioNotifierTest(TestCase):
    def test_new_notifier(self):
        configuration = Mock(Configuration)
        notifier = Mock(Notifier)
        notifier = new_notifier(configuration, notifier, PluginConfiguration('stdio'))
        self.assertIsInstance(notifier, StdioNotifier)
