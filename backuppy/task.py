"""Code to run back-ups."""
import subprocess


def backup(configuration, notifier, source, target):
    """Start a new back-up.

    :param configuration: Configuration
    :param notifier: Notifier
    :param source: Location
    :param target: Location
    """
    notifier.state('Initializing back-up %s' % configuration.name)

    if not source.is_available():
        notifier.alert('No back-up source available.')
        return False

    if not target.is_available():
        notifier.alert('No back-up target available.')
        return False

    notifier.inform('Backing up %s...' % configuration.name)

    args = ['rsync', '-ar', '--numeric-ids', '-e', 'ssh -i $ssh_key']
    if configuration.verbose:
        args.append('--verbose')
        args.append('--progress')
    args.append(source.to_rsync())
    args.append(target.to_rsync())
    subprocess.call(args)

    notifier.confirm('Back-up %s complete.' % configuration.name)

    return True
