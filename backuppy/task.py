"""Code to run back-ups."""


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
        return None

    if not target.is_available():
        notifier.alert('No back-up target available.')
        return None

    notifier.inform('Backing up %s...' % configuration.name)
