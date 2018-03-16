import os
import subprocess
from unittest import TestCase

from parameterized import parameterized

from backuppy.cli import main, FORMAT_JSON_EXTENSIONS, FORMAT_YAML_EXTENSIONS
from backuppy.config import from_json, from_yaml
from backuppy.location import PathSource, PathTarget
from backuppy.tests import CONFIGURATION_PATH

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from backports.tempfile import TemporaryDirectory


class CliTest(TestCase):
    def test_help_appears_in_readme(self):
        """Assert that the CLI command's help output in README.md is up-to-date."""
        cli_help = subprocess.check_output(
            ['backuppy', '--help']).decode('utf-8')
        readme_path = os.path.join(os.path.dirname(
            os.path.dirname(os.path.dirname(__file__))), 'README.md')
        with open(readme_path) as f:
            self.assertIn(cli_help, f.read())


class CliBackupTest(TestCase):
    def test_backup_with_json(self):
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        args = ['backup', '-c', configuration_file_path]
        main(args)

    def test_backup_with_yaml(self):
        configuration_file_path = '%s/backuppy.yml' % CONFIGURATION_PATH
        args = ['backup', '-c', configuration_file_path]
        main(args)

    def test_backup_without_arguments(self):
        args = ['backup']
        with self.assertRaises(SystemExit):
            main(args)


class CliInitTest(TestCase):
    @parameterized.expand([
        (True, 'yaml'),
        (True, 'yaml'),
        (False, 'json'),
        (False, 'json'),
    ])
    @patch('backuppy.cli._input')
    @patch('sys.stdout')
    @patch('sys.stderr')
    def test_init(self, verbose, format, m_stderr, m_stdout, m_input):
        name = 'Home is where the Bart is'
        source_path = '/tmp/Foo/Baz_bar_source'
        target_path = '/tmp/Foo/Baz_bar_target'
        with TemporaryDirectory() as working_directory:
            configuration_file_path = os.path.join(working_directory, 'backuppy.' + format)
            file_path_extensions = FORMAT_YAML_EXTENSIONS if 'yaml' == format else FORMAT_JSON_EXTENSIONS
            file_path_extensions_label = ', '.join(map(lambda x: '*.' + x, file_path_extensions))
            m_input.side_effect = lambda *args: {
                ('Name: ',): name,
                ('Verbose output [Y/n]: ',): 'y' if verbose else 'n',
                ('File format (0-1): ',): '0' if 'yaml' == format else '1',
                ('Destination (%s): ' % file_path_extensions_label,): configuration_file_path,
                ('Source path: ',): source_path,
                ('Target path: ',): target_path,
            }[args]
            args = ['init']
            main(args)
            with open(configuration_file_path) as f:
                factory = from_yaml if 'yaml' == format else from_json
                configuration = factory(f)
                self.assertEquals(configuration.name, name)
                self.assertEquals(configuration.verbose, verbose)
                source = configuration.source
                self.assertIsInstance(source, PathSource)
                self.assertEquals(source.path, source_path)
                target = configuration.target
                self.assertIsInstance(target, PathTarget)
                self.assertEquals(target.path, target_path)
