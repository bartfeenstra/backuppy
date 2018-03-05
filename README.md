# Backuppy

[![Build Status](https://travis-ci.org/bartfeenstra/backuppy.svg?branch=master)](https://travis-ci.org/bartfeenstra/backuppy) [![Coverage Status](https://coveralls.io/repos/github/bartfeenstra/backuppy/badge.svg?branch=master)](https://coveralls.io/github/bartfeenstra/backuppy?branch=master) ![Backuppy runs on Python 2.7, 3.5, and 3.6](https://img.shields.io/badge/Python-2.7%2C%203.5%2C%203.6-blue.svg) ![Latest Git tag](https://img.shields.io/github/tag/bartfeenstra/backuppy.svg) ![Backuppy is released under the MIT license](https://img.shields.io/github/license/bartfeenstra/backuppy.svg)

## About
Backuppy back-ups and restores your data using Rsync, allowing different routes to the same, or different destinations.

## License
Backuppy is released under the [MIT](./LICENSE) license.

## Requirements
- Python 2.7+
- Bash

## Usage
```bash
$ backuppy --help
usage: backuppy [-h] -c CONFIGURATION

Backs up your data.

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGURATION, --configuration CONFIGURATION
                        The path to the back-up configuration file.
```
