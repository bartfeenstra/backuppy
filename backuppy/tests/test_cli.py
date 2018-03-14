import json
import os
import subprocess
from logging import Logger
from tempfile import NamedTemporaryFile
from unittest import TestCase

from parameterized import parameterized

from backuppy.cli import main
from backuppy.tests import CONFIGURATION_PATH

try:
    from unittest.mock import patch, call, Mock
except ImportError:
    from mock import patch, call, Mock


class CliTest(TestCase):
    def test_help_appears_in_readme(self):
        """Assert that the CLI command's help output in README.md is up-to-date."""
        cli_help = subprocess.check_output(['backuppy', '--help']).decode('utf-8')
        readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'README.md')
        with open(readme_path) as f:
            self.assertIn(cli_help, f.read())

    @patch('sys.stdout')
    @patch('sys.stderr')
    def test_backup_with_json(self, m_stdout, m_stderr):
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        args = ['backup', '-c', configuration_file_path]
        main(args)

    @patch('sys.stdout')
    @patch('sys.stderr')
    def test_backup_with_yaml(self, m_stdout, m_stderr):
        configuration_file_path = '%s/backuppy.yml' % CONFIGURATION_PATH
        args = ['backup', '-c', configuration_file_path]
        main(args)

    @patch('sys.stdout')
    @patch('sys.stderr')
    def test_backup_without_arguments(self, m_stdout, m_stderr):
        args = ['backup']
        with self.assertRaises(SystemExit):
            main(args)

    @patch('sys.stdout')
    @patch('sys.stderr')
    @patch('backuppy.task.backup')
    def test_keyboard_interrupt_in_command_should_exit_gracefully(self, m_backup, m_stderr, m_stdout):
        m_backup.side_effect = KeyboardInterrupt
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        args = ['backup', '-c', configuration_file_path]
        main(args)
        m_stdout.write.assert_has_calls([call('Quitting...')])
        m_stderr.write.assert_not_called()

    @parameterized.expand([
        (ValueError,),
        (RuntimeError,),
        (AttributeError,),
        (ImportError,),
        (NotImplementedError,),
    ])
    @patch('sys.stdout')
    @patch('sys.stderr')
    @patch('backuppy.task.backup')
    @patch('logging.getLogger')
    def test_error_in_command(self, error_type, m_get_logger, m_backup, m_stderr, m_stdout):
        m_backup.side_effect = error_type
        m_logger = Mock(Logger)
        m_get_logger.return_value = m_logger
        with open('%s/backuppy.json' % CONFIGURATION_PATH) as f:
            configuration = json.load(f)
        configuration['notifications'] = [
            {
                'type': 'stdio',
            }
        ]
        with NamedTemporaryFile(mode='w+t', suffix='.json') as f:
            json.dump(configuration, f)
            f.seek(0)
            args = ['backup', '-c', f.name]
            main(args)
            m_get_logger.assert_called_with('backuppy')
            self.assertTrue(m_logger.exception.called)
            m_stderr.write.assert_has_calls([
                call(
                    '\x1b[0;41m  \x1b[0;1;31m A fatal error occurred. Details have been logged as per your configuration.\x1b[0m'),
            ])
