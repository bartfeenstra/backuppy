"""Provide CLI components."""
import argparse
import re

import subprocess

import os


class SemanticVersionAction(argparse.Action):
    """Provide a Semantic Version action."""

    def __call__(self, parser, namespace, values, option_string=None):
        """Invoke the action."""
        if re.search('^\d+\.\d+\.\d+$', values) is None:
            raise ValueError('Must be a Semantic Version (x.y.z). See https://semver.org/.')
        setattr(namespace, self.dest, values)


def main(args):
    """Provide the CLI entry point."""
    parser = argparse.ArgumentParser(description='Backs up your data.')
    parser.add_argument('--version', action=SemanticVersionAction, required=True,
                        help='The version to release.')
    cli_args = vars(parser.parse_args(args))
    version = cli_args['version']
    project_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    _is_ready(project_path, version)
    _tag(project_path, version)
    _build(project_path)
    _publish(project_path)
    print('Done.')


def _is_ready(project_path, version):
    # Check this version does not already exist.
    tags = subprocess.check_output(['git', 'tag'], cwd=project_path).split()
    if version in tags:
        raise RuntimeError('Version %s already exists.' % version)

    # Check there are no uncommitted changes.
    p = subprocess.Popen(['git', 'diff-index', '--quiet', 'HEAD', '--'], cwd=project_path)
    code = p.wait()
    if 0 != code:
        subprocess.call(['git', 'status'], cwd=project_path)
        raise RuntimeError('The Git repository has uncommitted changes.')


def _tag(project_path, version):
    with open('/'.join([project_path, 'VERSION']), mode='w+t') as f:
        f.write(version)
    subprocess.call(['git', 'add', 'VERSION'], cwd=project_path)
    subprocess.call(['git', 'commit', '-m', 'Release version %s.' % version], cwd=project_path)
    subprocess.call(['git', 'tag', version], cwd=project_path)
    subprocess.call(['git', 'push', '--tags'], cwd=project_path)


def _build(project_path):
    subprocess.call(['python', 'setup.py', 'bdist_wheel', '--universal'], cwd=project_path)


def _publish(project_path):
    subprocess.call(['twine', 'upload', './dist/*'], cwd=project_path)
