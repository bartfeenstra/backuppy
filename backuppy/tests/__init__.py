import os

RESOURCE_PATH = '/'.join(
    (os.path.dirname(os.path.abspath(__file__)), 'resources'))

CONFIGURATION_PATH = '/'.join((RESOURCE_PATH, 'configuration'))
