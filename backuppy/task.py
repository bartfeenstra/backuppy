"""Code to run back-ups."""
import subprocess

import os

from backuppy.config import Configuration
from backuppy.location import new_snapshot_name, Path, FilePath, DirectoryPath


def backup(configuration, path=None):
    """Start a new back-up.

    :param configuration: Configuration
    :param path: backuppy.location.Path
    """
    assert isinstance(configuration, Configuration)
    assert path is None or isinstance(path, Path)
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

    args = ['rsync', '-ar', '--numeric-ids',
            '-e', 'ssh -o StrictHostKeyChecking=yes']
    if configuration.verbose:
        args.append('--verbose')
        args.append('--progress')
    args.append(source.to_rsync(path))
    if isinstance(path, FilePath):
        args.append(target.to_rsync(DirectoryPath(
            os.path.dirname(str(path)) + '/')))
    else:
        args.append(target.to_rsync(path))
    subprocess.call(args)

    notifier.confirm('Back-up %s complete.' % configuration.name)

    return True


def restore(configuration, path=None):
    """Restores a back-up.

    :param configuration: Configuration
    :param path: backuppy.location.Path
    """
    assert isinstance(configuration, Configuration)
    assert path is None or isinstance(path, Path)
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

    args = ['rsync', '-ar', '--numeric-ids',
            '-e', 'ssh -o StrictHostKeyChecking=yes']
    if configuration.verbose:
        args.append('--verbose')
        args.append('--progress')
    args.append(target.to_rsync(path))
    if isinstance(path, FilePath):
        args.append(source.to_rsync(DirectoryPath(
            os.path.dirname(str(path)) + '/')))
    else:
        args.append(source.to_rsync(path))
    subprocess.call(args)

    notifier.confirm('Restoration of back-up %s complete.' %
                     configuration.name)

    return True
