from unittest import TestCase

from backuppy.cli.backuppy import main
from backuppy.tests import CONFIGURATION_PATH


class CliTest(TestCase):
    def test_with_json(self):
        configuration_file_path = '%s/backuppy.json' % CONFIGURATION_PATH
        args = ['-c', configuration_file_path]
        main(args)

    def test_with_yaml(self):
        configuration_file_path = '%s/backuppy.yml' % CONFIGURATION_PATH
        args = ['-c', configuration_file_path]
        main(args)

    def test_without_arguments(self):
        args = []
        with self.assertRaises(SystemExit):
            main(args)
