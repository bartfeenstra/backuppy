# Backuppy

[![Build Status](https://travis-ci.org/bartfeenstra/backuppy.svg?branch=master)](https://travis-ci.org/bartfeenstra/backuppy) [![Coverage Status](https://coveralls.io/repos/github/bartfeenstra/backuppy/badge.svg?branch=master)](https://coveralls.io/github/bartfeenstra/backuppy?branch=master)

## About
Backuppy back-ups and restores your data using Rsync, allowing different routes to the same, or different destinations.

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
