import os


def assert_path(test, actual_path, expected_path):
    """Assert two actual and expected directory paths are identical.

    :param test: unittest.TestCase
    :param actual_path: str
    :param expected_path: str
    :raise: AssertionError
    """
    actual_path = actual_path.rstrip('/') + '/'
    expected_path = expected_path.rstrip('/') + '/'
    try:
        for expected_dir_path, child_dir_names, child_file_names in os.walk(expected_path):
            actual_dir_path = os.path.join(actual_path, expected_dir_path[len(expected_path):])
            for child_file_name in child_file_names:
                with open(os.path.join(expected_dir_path, child_file_name)) as expected_f:
                    with open(os.path.join(actual_dir_path, child_file_name)) as actual_f:
                        assert_file(test, actual_f, expected_f)
    except Exception:
        raise AssertionError(
            'The actual contents under the path `%s` are not equal to the expected contents under `%s`.' % (
                actual_path, expected_path))


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
