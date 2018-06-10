"""Code to run back-ups."""
import subprocess

from backuppy.config import Configuration
from backuppy.location import new_snapshot_name


def rsync(configuration, origin, destination, path=None):
    """Invoke rsync.

    :raise: subprocess.CalledProcessError
    """
    args = ['rsync', '-ar', '--numeric-ids', '--relative']

    ssh_options = configuration.ssh_options()
    if ssh_options:
        ssh_args = []
        for option, value in ssh_options.items():
            ssh_args.append('-o %s=%s' % (option, value))
        args.append('-e')
        args.append('ssh %s' % ' '.join(ssh_args))

    if configuration.verbose:
        args.append('--verbose')
        args.append('--progress')

    if path is None:
        path = ''
    args.append('%s./%s' % (origin.to_rsync(), path))
    args.append(destination.to_rsync())

    subprocess.check_call(args)


def backup(configuration, path=None):
    """Start a new back-up.

    :param configuration: Configuration
    :param path: str
    """
    assert isinstance(configuration, Configuration)
    notifier = configuration.notifier
    source = configuration.source
    target = configuration.target

    notifier.state('Initializing back-up %s' % configuration.name)

    if not source.is_available():
        notifier.alert('No back-up source available.')
        return False

    if not target.is_available():
        notifier.alert('No back-up target available.')
        return False

    notifier.inform('Backing up %s...' % configuration.name)

    snapshot_name = new_snapshot_name()
    target.snapshot(snapshot_name)

    try:
        rsync(configuration, source, target, path)
        notifier.confirm('Back-up %s complete.' % configuration.name)
        return True
    except subprocess.CalledProcessError:
        configuration.logger.exception('An rsync error occurred.')
        notifier.confirm('Back-up %s failed.' % configuration.name)
        return False


def restore(configuration, path=None):
    """Restores a back-up.

    :param configuration: Configuration
    :param path: str
    """
    assert isinstance(configuration, Configuration)
    notifier = configuration.notifier
    source = configuration.source
    target = configuration.target

    notifier.state('Initializing restoration of back-up %s' %
                   configuration.name)

    if not source.is_available():
        notifier.alert('No back-up source available.')
        return False

    if not target.is_available():
        notifier.alert('No back-up target available.')
        return False

    notifier.inform('Restoring %s...' % configuration.name)

    try:
        rsync(configuration, target, source, path)
        notifier.confirm('Restoration of back-up %s complete.' % configuration.name)
        return True
    except subprocess.CalledProcessError:
        configuration.logger.exception('An rsync error occurred.')
        notifier.alert('Restoration of back-up %s failed.' % configuration.name)
        return False
