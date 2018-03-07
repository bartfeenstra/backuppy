"""Integrates Backuppy with Python's setuptools."""

import os
from setuptools import setup, find_packages

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

with open('/'.join((ROOT_PATH, 'VERSION'))) as f:
    VERSION = f.read()

with open('/'.join((ROOT_PATH, 'requirements.txt'))) as f:
    DEPENDENCIES = f.read().split("\n")

SETUP = {
    'name': "backuppy",
    'description': 'A back-up tool.',
    'long_description': open('README.md').read(),
    'version': VERSION,
    'license': "MIT",
    'author': "Bart Feenstra",
    'url': "https://github.com/bartfeenstra/backuppy",
    'install_requires': DEPENDENCIES,
    'packages': find_packages(),
    'scripts': [
        'bin/backuppy',
    ],
}

if __name__ == '__main__':
    setup(**SETUP)
