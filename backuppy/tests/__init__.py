import os
import subprocess
from tempfile import NamedTemporaryFile

from backuppy.location import SshTarget, SshSource

RESOURCE_PATH = '/'.join(
    (os.path.dirname(os.path.abspath(__file__)), 'resources'))

CONFIGURATION_PATH = '/'.join((RESOURCE_PATH, 'configuration'))


def build_files_stage_1(path):
    """Build a directory structure with files to back up.

    :param path: str
    """
    with open(os.path.join(path, 'some.file'), mode='w+t') as f:
        f.write('This is just some file...')
        f.flush()
    os.makedirs(os.path.join(path, 'sub'))
    with open(os.path.join(path, 'sub', 'some.file.in.subdirectory'), mode='w+t') as f:
        f.write('This is just some other file in a subdirectory...')
        f.flush()


def build_files_stage_2(path):
    """Extend a directory structure with files to back up.

    This should be called after build_files_stage_1().

    :param path: str
    """
    with open(os.path.join(path, 'sub', 'some.file.in.subdirectory'), mode='w+t') as f:
        f.write(
            'This is just some other file in a subdirectory that we made some changes to...')
        f.flush()
    with open(os.path.join(path, 'some.later.file'), mode='w+t') as f:
        f.write('These contents were added much later.')
        f.flush()


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


class SshLocationContainer(object):
    """Run a Docker container to serve as an SSH location."""

    NAME = 'backuppy_test'
    PORT = 22
    USERNAME = 'root'
    PASSWORD = 'root'
    IDENTITY = os.path.join(RESOURCE_PATH, 'id_rsa')
    PATH = '/backuppy/'

    def __init__(self, mount_point=None):
        """Initialize a new instance."""
        self._started = False
        self._ip = None
        self._fingerprint = None
        self._known_hosts = None
        self._mount_point = mount_point

    def _ensure_started(self):
        """Ensure the container has been started."""
        if not self._started:
            raise RuntimeError('This container has not been started yet.')

    def start(self):
        """Start the container."""
        docker_args = []
        if self._mount_point is not None:
            docker_args += ['-v', '%s:%s' %
                            (self._mount_point, self.PATH)]
        self.stop()
        subprocess.check_call(['docker', 'run', '-d', '--name',
                               self.NAME] + docker_args + ['backuppy_ssh_location'])
        self._started = True
        self.await()
        subprocess.check_call(['sshpass', '-p', self.PASSWORD, 'scp', '-o', 'UserKnownHostsFile=%s' % self.known_hosts(
        ).name, '%s.pub' % self.IDENTITY, '%s@%s:~/.ssh/authorized_keys' % (self.USERNAME, self.ip)])

    def stop(self):
        """Stop the container."""
        if not self._started:
            return
        self._started = False
        subprocess.check_call(['docker', 'stop', self.NAME])
        subprocess.check_call(['docker', 'container', 'rm', self.NAME])
        self._known_hosts.close()

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
        if self._known_hosts:
            return self._known_hosts

        self._known_hosts = NamedTemporaryFile(mode='r+')
        self._known_hosts.write(self.fingerprint)
        self._known_hosts.flush()
        return self._known_hosts

    def await(self):
        """Wait until the container is ready."""
        subprocess.check_call(['./bin/wait-for-it', '%s:%d' % (self.ip, self.PORT)])

    def source(self, configuration):
        """Get the back-up source to this container.

        :return: backuppy.location.Source
        """
        return SshSource(configuration.notifier, self.USERNAME, self.ip, self.PATH, identity=self.IDENTITY, host_keys=self.known_hosts().name)

    def target(self, configuration):
        """Get the back-up target to this container.

        :return: backuppy.location.Target
        """
        return SshTarget(configuration.notifier, self.USERNAME, self.ip, self.PATH, identity=self.IDENTITY, host_keys=self.known_hosts().name)
