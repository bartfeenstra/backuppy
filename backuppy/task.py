"""Code to run back-ups."""
import subprocess

from backuppy.config import Configuration
from backuppy.location import Source, Target
from backuppy.notifier import Notifier


def backup(configuration, notifier, source, target):
    """Start a new back-up.

    :param configuration: Configuration
    :param notifier: Notifier
    :param source: Source
    :param target: Target
    """
    assert isinstance(configuration, Configuration)
    assert isinstance(notifier, Notifier)
    assert isinstance(source, Source)
    assert isinstance(target, Target)

    notifier.state('Initializing back-up %s' % configuration.name)

    if not source.is_available():
        notifier.alert('No back-up source available.')
        return False

    if not target.is_available():
        notifier.alert('No back-up target available.')
        return False

    notifier.inform('Backing up %s...' % configuration.name)

    target.snapshot()

    args = ['rsync', '-ar', '--numeric-ids']
    if configuration.verbose:
        args.append('--verbose')
        args.append('--progress')
    args.append(source.to_rsync())
    args.append(target.to_rsync())
    subprocess.call(args)

    notifier.confirm('Back-up %s complete.' % configuration.name)

    return True
