from unittest import TestCase
try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from backuppy.notifier import NotifySendNotifier


class NotifySendNotifierTest(TestCase):
    @patch('subprocess.call')
    def test_notify(self, m):
        sut = NotifySendNotifier()
        message = 'Something happened!'
        sut.notify(message)
        m.assert_called_with(('notify-send', "'%s'" % message))
