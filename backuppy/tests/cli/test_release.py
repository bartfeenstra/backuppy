from unittest import TestCase

from backuppy.cli.release import main


class CliTest(TestCase):
    def test_without_semantic_version(self):
        args = ['--version', 'foo']
        with self.assertRaises(ValueError):
            main(args)

    def test_without_arguments(self):
        args = []
        with self.assertRaises(SystemExit):
            main(args)
