import os
from setuptools import setup, find_packages

VERSION = '0.0.1'

REQUIREMENTS_PATH = '/'.join((os.path.dirname(os.path.abspath(__file__)), 'requirements.txt'))

# with open(REQUIREMENTS_PATH) as f:
#     dependencies = f.read().split("\n")

SETUP = {
    'name': "backuppy",
    'description': 'A back-up tool.',
    # 'long_description': open('README.md').read(),
    'version': VERSION,
    'license': "MIT",
    'author': "Bart Feenstra",
    'url': "https://github.com/bartfeenstra/backuppy",
    # 'install_requires': dependencies,
    'packages': find_packages(),
}

if __name__ == '__main__':
    setup(**SETUP)
