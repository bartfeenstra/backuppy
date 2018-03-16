import os


def assert_path(test, source_path, target_path):
    """Assert two source and target directory paths are identical.

    :param test: unittest.TestCase
    :param source_path: str
    :param target_path: str
    :raise: AssertionError
    """
    try:
        for source_dir_path, child_dir_names, child_file_names in os.walk(source_path):
            target_dir_path = target_path + source_dir_path[len(source_path):]
            for child_file_name in child_file_names:
                with open(os.path.join(source_dir_path, child_file_name)) as source_f:
                    with open(os.path.join(target_dir_path, child_file_name)) as target_f:
                        assert_file(test, source_f, target_f)
    except Exception:
        raise AssertionError(
            'The paths `%` and `%s` and their contents are not equal.')


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
