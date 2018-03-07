"""Provide CLI components."""
import argparse
import re

import subprocess

import os


class SemanticVersionAction(argparse.Action):
    """Provide a Semantic Version action."""

    def __call__(self, parser, namespace, values, option_string=None):
        """Invoke the action."""
        if not re.fullmatch('^\d+\.\d+\.\d+$', values):
            raise ValueError('Must be a Semantic Version (x.y.z). See https://semver.org/.')
        setattr(namespace, self.dest, values)


def main(args):
    """Provide the CLI entry point."""
    parser = argparse.ArgumentParser(description='Backs up your data.')
    parser.add_argument('--version', action=SemanticVersionAction, required=True,
                        help='The version to release.')
    cli_args = vars(parser.parse_args(args))
    version = cli_args['version']
    _is_ready(version)
    _tag(version)
    _build(version)
    _publish(version)
    print('Done.')


def _is_ready(version):
    # Check this version does not already exist.
    tags = subprocess.check_output(['git', 'tag']).split()
    if version in tags:
        raise RuntimeError('Version %s already exists.' % version)

    # Check there are no uncommitted changes.
    p = subprocess.Popen(['git', 'diff-index', '--quiet', 'HEAD', '--'])
    code = p.wait()
    if 0 != code:
        subprocess.call(['git', 'status'])
        raise RuntimeError('The Git repository has uncommitted changes.')


def _tag(version):
    root_path = os.path.dirname(__file__)
    with open('/'.join([root_path, 'VERSION']), mode='w+t') as f:
        f.write(version)
    subprocess.call(['git', 'add', 'VERSION'], cwd=root_path)
    subprocess.call(['git', 'commit', '-m', 'Release version %s.' % version], cwd=root_path)
    subprocess.call(['git', 'tag', version])
    subprocess.call(['git', 'push', '--tags'])


def _build(version):
    pass


def _publish(version):
    pass
