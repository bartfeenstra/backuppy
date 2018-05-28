import os
import subprocess
from tempfile import NamedTemporaryFile

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


class SshTargetContainer(object):
    """Run a Docker container to serve as an SSH target."""

    NAME = 'backuppy_test'
    PORT = 22
    USERNAME = 'root'
    PASSWORD = 'root'
    IDENTITY = os.path.join(RESOURCE_PATH, 'id_rsa')

    def __init__(self):
        """Initialize a new instance."""
        self._started = False
        self._ip = None
        self._fingerprint = None

    def _ensure_started(self):
        """Ensure the container has been started."""
        if not self._started:
            raise RuntimeError('This container has not been started yet.')

    def start(self):
        """Start the container."""
        self.stop()
        subprocess.call(['docker', 'run', '-d', '--name',
                         self.NAME, 'rastasheep/ubuntu-sshd:18.04'])
        self._started = True
        self.await()
        with self.known_hosts() as f:
            subprocess.call(['sshpass', '-p', self.PASSWORD, 'scp', '-o', 'UserKnownHostsFile=%s' %
                             f.name, '%s.pub' % self.IDENTITY, '%s@%s:~/.ssh/authorized_keys' % (self.USERNAME, self.ip)])

    def stop(self):
        """Stop the container."""
        self._started = False
        subprocess.call(['docker', 'stop', self.NAME])
        subprocess.call(['docker', 'container', 'rm', self.NAME])

    @property
    def ip(self):
        """Get the container's IP address.

        :return: str
        """
        self._ensure_started()

        if not self._ip:
            self._ip = str(subprocess.check_output(
                ['docker', 'inspect', '-f', '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}',
                 self.NAME]).strip().decode('utf-8'))

        return self._ip

    @property
    def fingerprint(self):
        """Get the container's SSH host key fingerprint.

        :return: str
        """
        self._ensure_started()

        if not self._fingerprint:
            self._fingerprint = str(subprocess.check_output(
                ['ssh-keyscan', '-t', 'rsa', self.ip]).decode('utf-8'))

        return self._fingerprint

    def known_hosts(self):
        """Get an SSH known_hosts file containing just this container.

        :return: File
        """
        f = NamedTemporaryFile(mode='r+')
        f.write(self.fingerprint)
        f.flush()
        return f

    def await(self):
        """Wait until the container is ready."""
        subprocess.call(['./bin/wait-for-it', '%s:%d' % (self.ip, self.PORT)])
