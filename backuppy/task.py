"""Code to run back-ups."""
import subprocess

from backuppy.config import Configuration


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
