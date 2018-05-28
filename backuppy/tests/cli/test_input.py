from unittest import TestCase

from parameterized import parameterized

from backuppy.cli.input import ask_confirm, ask_option, ask_any

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch


class AskConfirmTest(TestCase):
    @parameterized.expand([
        (True, 'Foo (y/n): ', 'y', 'Foo', None, None),
        (True, 'Foo (y/n): ', 'Y', 'Foo', None, None),
        (False, 'Foo (y/n): ', 'n', 'Foo', None, None),
        (True, 'Foo [Y/n]: ', '', 'Foo', None, True),
        (False, 'Foo [y/N]: ', '', 'Foo', None, False),
    ])
    @patch('backuppy.cli.input._input')
    def test_ask_confirm(self, expected, prompt, raw_input, value_label, question, default, m_input):
        m_input.side_effect = lambda *args: {
            (prompt,): raw_input,
        }[args]
        actual = ask_confirm(value_label, question=question, default=default)
        self.assertEquals(actual, expected)


class AskOptionTest(TestCase):
    options = [
        ('option_a', 'This is option A.'),
        ('option_b', 'This is the runner-up.'),
        ('option_c', 'Last, but certainly not least!'),
    ]

    @parameterized.expand([
        ('option_a', '0', 'Foo', None, options),
        ('option_b', '1', 'Foo', None, options),
        ('option_c', '2', 'Foo', None, options),
    ])
    @patch('backuppy.cli.input._input')
    def test_ask_option(self, expected, cli_input, value_label, question, options, m_input):
        m_input.side_effect = lambda *args: {
            ('Foo (0-2): ',): cli_input,
        }[args]
        actual = ask_option(value_label, options, question=question)
        self.assertEquals(actual, expected)

    def test_ask_option_with_one_option(self):
        options = [
            ('some_option', 'Something, yeah...'),
        ]
        actual = ask_option('Choose wisely', options)
        self.assertEquals(actual, 'some_option')


class AskAnyTest(TestCase):
    @patch('backuppy.cli.input._input')
    def test_ask_any_optional(self, m_input):
        m_input.side_effect = lambda *args: {
            ('Foo: ',): '',
        }[args]
        actual = ask_any('Foo', required=False)
        self.assertEquals(actual, '')

    @patch('backuppy.cli.input._input')
    def test_ask_any_required(self, m_input):
        m_input.side_effect = lambda *args: {
            ('Foo: ',): 'Bar',
        }[args]
        actual = ask_any('Foo', required=True)
        self.assertEquals(actual, 'Bar')

    @patch('backuppy.cli.input._input')
    def test_ask_any_with_validator(self, m_input):
        m_input.side_effect = lambda *args: {
            ('Foo: ',): 'Bar',
        }[args]

        def _validator(value):
            return value + 'Baz'

        actual = ask_any('Foo', validator=_validator)
        self.assertEquals(actual, 'BarBaz')
