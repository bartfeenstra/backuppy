"""Provide CLI components."""
import argparse
import os
import re
import subprocess


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

    # Prepare the workspace directories.
    subprocess.call(['rm', '-rf', 'backuppy.egg-info', 'build', 'dist'], cwd=project_path)

    # Create the release branch.
    branch = 'release-' + version
    subprocess.call(['git', 'checkout', '-b', branch], cwd=project_path)

    # Commit the release to Git.
    with open('/'.join([project_path, 'VERSION']), mode='w+t') as f:
        f.write(version)
    subprocess.call(['git', 'add', 'VERSION'], cwd=project_path)
    subprocess.call(['git', 'commit', '-m', 'Release version %s.' % version], cwd=project_path)
    subprocess.call(['git', 'tag', version], cwd=project_path)

    # Build and publish the package.
    subprocess.call(['python', 'setup.py', 'bdist_wheel', '--universal'], cwd=project_path)
    subprocess.call(['twine', 'upload', './dist/*'], cwd=project_path)

    # Revert back to a development state.
    subprocess.call(['git', 'revert', '--no-edit', 'HEAD'], cwd=project_path)

    # Push changes.
    subprocess.call(['git', 'push', '--set-upstream', 'origin', branch], cwd=project_path)
    subprocess.call(['git', 'push', '--tags'], cwd=project_path)

    print(
        'Finalize the %s release by approving and merging its pull request at https://github.com/bartfeenstra/backuppy/compare/release-%s?expand=1.' % (
            version, version))
