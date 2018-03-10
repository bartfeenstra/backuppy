# Backuppy

[![Build Status](https://travis-ci.org/bartfeenstra/backuppy.svg?branch=master)](https://travis-ci.org/bartfeenstra/backuppy) [![Coverage Status](https://coveralls.io/repos/github/bartfeenstra/backuppy/badge.svg?branch=master)](https://coveralls.io/github/bartfeenstra/backuppy?branch=master) ![Backuppy runs on Python 2.7, 3.5, and 3.6](https://img.shields.io/badge/Python-2.7%2C%203.5%2C%203.6-blue.svg) ![Latest Git tag](https://img.shields.io/github/tag/bartfeenstra/backuppy.svg) ![Backuppy is released under the MIT license](https://img.shields.io/github/license/bartfeenstra/backuppy.svg)

## About
Backuppy backs up and restores your data using rsync, allowing different routes to the same, or different destinations.

The following instructions can be executed in any system Python environment, but you may want to use a
[virtual environment](https://docs.python.org/3/library/venv.html). Alternatively, some actions can be performed using
[tox](https://tox.readthedocs.io/) as well, which produces its own virtual environments in `.tox/py**`.

## License
Backuppy is released under the [MIT](./LICENSE) license.

## Usage

### Requirements
- Python 2.7+

### Installation
In any Python environment, run `pip install backuppy`.

### Command line
```bash
$ backuppy --help
usage: backuppy [-h] -c CONFIGURATION

Backs up your data.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGURATION, --configuration CONFIGURATION
                        The path to the back-up configuration file.
```

### Configuration file
Configuration files are written in YAML or JSON, and can be stored anywhere as `*.yml`, `*.yaml`, or `*.json`.
[View example](./backuppy/tests/resources/configuration/backuppy.json).

## Development

### Requirements
- The generic requirements documented earlier.
- Bash (you're all good if `which bash` outputs a path in your terminal)

### Installation
Run `git clone https://github.com/bartfeenstra/backuppy.git`.

If you wish to contribute code changes, you may want to fork this project first, and clone your own forked repository
instead.

### Building
In any Python environment, run `./bin/build-dev`.

With tox, run `tox --develop --notest`.

### Testing
In any Python environment, run `./bin/test`.

With tox, run `tox --develop`

### Fixing problems automatically
In any Python environment, run `./bin/fix`.
