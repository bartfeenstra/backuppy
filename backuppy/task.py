"""Code to run back-ups."""
import subprocess

from backuppy.config import Configuration
from backuppy.location import new_snapshot_name


def backup(configuration):
    """Start a new back-up.

    :param configuration: Configuration
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

    args = ['rsync', '-ar', '--numeric-ids',
            '-e', 'ssh -o "StrictHostKeyChecking no"']
    if configuration.verbose:
        args.append('--verbose')
        args.append('--progress')
    args.append(source.to_rsync())
    args.append(target.to_rsync())
    subprocess.call(args)

    notifier.confirm('Back-up %s complete.' % configuration.name)

    return True
