"""Parse command-line input."""
import re


def _input(prompt=None):
    """Wrap input() and raw_input() on Python 3 and 2 respectively.

    :param prompt: Optional[str]
    :return: str
    """
    try:
        return raw_input(prompt)
    except NameError:
        return input(prompt)


def ask_confirm(value_label, question=None, default=None):
    """Ask for a confirmation.

    :param value_label: str
    :param question: Optional[None]
    :param default: Optional[bool]
    :return: bool
    """
    if default is None:
        options_label = '(y/n)'
    elif default:
        options_label = '[Y/n]'
    else:
        options_label = '[y/N]'
    confirmation = None
    while confirmation is None:
        if question is not None:
            print(question)
        confirmation_input = _input('%s %s: ' % (
            value_label, options_label)).lower()
        if 'y' == confirmation_input:
            confirmation = True
        elif 'n' == confirmation_input:
            confirmation = False
        elif '' == confirmation_input and default is not None:
            confirmation = default
        else:
            print('That is not a valid confirmation. Enter "y" or "n".')
    return confirmation


def ask_any(value_label, question=None, required=True, validator=None):
    """Ask for any value.

    :param value_label: str
    :param question: Optional[None]
    :param required: Optional[bool]
    :param validator: Optional[Callable]
    :return: bool
    """
    string = None
    while string is None:
        if question is not None:
            print(question)
        string_input = _input(value_label + ': ')
        if validator:
            string = validator(string_input)
        elif not required or len(string_input):
            string = string_input
        else:
            print('You are required to enter a value.')
    return string


def ask_option(value_label, options, question=None):
    """Ask for a single item to be chosen from a collection.

    :param value_label: str
    :param options: Iterable[Tuple[Any, str]]
    :param question: Optional[None]
    :return: bool
    """
    if len(options) == 1:
        return options[0][0]

    option = None
    options_labels = []
    indexed_options = [(index, value, label)
                       for index, (value, label) in enumerate(options)]
    for index, _, option_label in indexed_options:
        options_labels.append('%d) %s' % (index, option_label))
    options_label = '0-%d' % (len(options) - 1)
    while option is None:
        if question is not None:
            print(question)
            print('\n'.join(options_labels))
        option_input = _input('%s (%s): ' % (value_label, options_label))
        try:
            if re.search('^\d+$', option_input) is None:
                raise IndexError()
            index_input = int(option_input)
            option = indexed_options[index_input][1]
        except IndexError:
            print('That is not a valid option. Enter %s.' % options_label)
    return option
