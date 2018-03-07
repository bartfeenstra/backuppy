"""Provide CLI components."""
import argparse

from backuppy.config import from_json
from backuppy.discover import new_location, new_notifier
from backuppy.location import FirstAvailableLocation
from backuppy.notifier import GroupedNotifiers, StdioNotifier
from backuppy.task import backup


def main(args):
    """Provide the CLI entry point."""
    parser = argparse.ArgumentParser(description='Backs up your data.')
    parser.add_argument('-c', '--configuration', action='store', required=True,
                        help='The path to the back-up configuration file.')
    cli_args = vars(parser.parse_args(args))
    configuration_file_path = cli_args['configuration']
    with open(configuration_file_path) as f:
        configuration = from_json(f)

        notifier = GroupedNotifiers([StdioNotifier()])
        for notifier_configuration in configuration.notifiers:
            notifier.notifiers.append(new_notifier(configuration, notifier, notifier_configuration))

        source = new_location(configuration, notifier, configuration.source)

        target = FirstAvailableLocation()
        for target_configuration in configuration.targets:
            target.locations.append(new_location(configuration, target, target_configuration))

        backup(configuration, notifier, source, target)
