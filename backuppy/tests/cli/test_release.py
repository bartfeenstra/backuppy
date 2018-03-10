import os
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

    def test_with_uncommitted_changes(self):
        file_name = __file__ + 'test'
        try:
            open(file_name, mode='w+t').close()
            args = ['--version', '0.0.0']
            with self.assertRaises(RuntimeError):
                main(args)
        finally:
            os.remove(file_name)
