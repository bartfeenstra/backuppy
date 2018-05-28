import os

RESOURCE_PATH = '/'.join(
    (os.path.dirname(os.path.abspath(__file__)), 'resources'))

CONFIGURATION_PATH = '/'.join((RESOURCE_PATH, 'configuration'))


def assert_paths_identical(test, source_path, target_path):
    """Assert the source and target directories are identical.

    :param test: unittest.TestCase
    :param source_path: str
    :param target_path: str
    :raise: AssertionError
    """
    assert_path_appears(test, source_path, target_path)
    assert_path_appears(test, target_path, source_path)


def assert_path_appears(test, source_path, target_path):
    """Assert the contents of one directory appear in another.

    :param test: unittest.TestCase
    :param source_path: str
    :param target_path: str
    :raise: AssertionError
    """
    source_path = source_path.rstrip('/') + '/'
    target_path = target_path.rstrip('/') + '/'
    try:
        for target_dir_path, child_dir_names, child_file_names in os.walk(target_path):
            source_dir_path = os.path.join(
                source_path, target_dir_path[len(target_path):])
            for child_file_name in child_file_names:
                with open(os.path.join(target_dir_path, child_file_name)) as target_f:
                    with open(os.path.join(source_dir_path, child_file_name)) as source_f:
                        assert_file(test, source_f, target_f)
    except Exception:
        raise AssertionError(
            'The source contents under the path `%s` are not equal to the target contents under `%s`.' % (
                source_path, target_path))


def assert_file(test, source_f, target_f):
    """Assert two source and target files are identical.

    :param test: unittest.TestCase
    :param source_f: File
    :param target_f: File
    :raise: AssertionError
    """
    source_f.seek(0)
    target_f.seek(0)
    test.assertEquals(source_f.read(), target_f.read())
