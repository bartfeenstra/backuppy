import json
from logging import Logger
from tempfile import NamedTemporaryFile
from unittest import TestCase

from backuppy.location import Source, Target
from backuppy.notifier import Notifier
from backuppy.tests import CONFIGURATION_PATH

try:
    from unittest.mock import Mock, patch
except ImportError:
    from mock import Mock, patch

from backuppy.config import Configuration, from_json, from_yaml, from_configuration_data


class ConfigurationTest(TestCase):
    def test_verbose(self):
        sut = Configuration('Foo', verbose=True)
        self.assertTrue(sut.verbose)
        sut.verbose = False
        self.assertFalse(sut.verbose)

    def test_working_directory(self):
        sut = Configuration('Foo', working_directory=CONFIGURATION_PATH)
        self.assertEquals(sut.working_directory, CONFIGURATION_PATH)

    def test_without_working_directory(self):
        sut = Configuration('Foo')
        with self.assertRaises(AttributeError):
            sut.working_directory

    def test_name_with_name(self):
        name = 'Foo'
        sut = Configuration(name)
        self.assertEquals(sut.name, name)

    def test_notifier(self):
        sut = Configuration('Foo')
        with self.assertRaises(AttributeError):
            sut.notifier
        notifier = Mock(Notifier)
        sut.notifier = notifier
        self.assertEquals(sut.notifier, notifier)
        with self.assertRaises(AttributeError):
            sut.notifier = notifier

    def test_source(self):
        sut = Configuration('Foo')
        with self.assertRaises(AttributeError):
            sut.source
        source = Mock(Source)
        sut.source = source
        self.assertEquals(sut.source, source)
        with self.assertRaises(AttributeError):
            sut.source = source

    def test_target(self):
        sut = Configuration('Foo')
        with self.assertRaises(AttributeError):
            sut.target
        target = Mock(Target)
        sut.target = target
        self.assertEquals(sut.target, target)
        with self.assertRaises(AttributeError):
            sut.target = target

    def test_logger(self):
        sut = Configuration('Foo')
        logger = sut.logger
        self.assertIsInstance(logger, Logger)


class FromConfigurationData(TestCase):
    def test_minimal(self):
        with open('%s/backuppy-minimal.json' % CONFIGURATION_PATH) as f:
            configuration = from_configuration_data(f.name, json.load(f))
            self.assertIsInstance(configuration, Configuration)

    def test_verbose_non_boolean(self):
        with open('%s/backuppy.json' % CONFIGURATION_PATH) as f:
            configuration = json.load(f)
        configuration['verbose'] = 666
        with NamedTemporaryFile(mode='w+t') as f:
            json.dump(configuration, f)
            with self.assertRaises(ValueError):
                from_configuration_data(f.name, configuration)

    def test_notifier_type_missing(self):
        with open('%s/backuppy.json' % CONFIGURATION_PATH) as f:
            configuration = json.load(f)
        del configuration['notifications'][0]['type']
        with NamedTemporaryFile(mode='w+t') as f:
            json.dump(configuration, f)
            with self.assertRaises(ValueError):
                from_configuration_data(f.name, configuration)

    def test_source_missing(self):
        with open('%s/backuppy.json' % CONFIGURATION_PATH) as f:
            configuration = json.load(f)
        del configuration['source']
        with NamedTemporaryFile(mode='w+t') as f:
            json.dump(configuration, f)
            with self.assertRaises(ValueError):
                from_configuration_data(f.name, configuration)

    def test_source_type_missing(self):
        with open('%s/backuppy.json' % CONFIGURATION_PATH) as f:
            configuration = json.load(f)
        del configuration['source']['type']
        with NamedTemporaryFile(mode='w+t') as f:
            json.dump(configuration, f)
            with self.assertRaises(ValueError):
                from_configuration_data(f.name, configuration)

    def test_target_missing(self):
        with open('%s/backuppy.json' % CONFIGURATION_PATH) as f:
            configuration = json.load(f)
        del configuration['target']
        with NamedTemporaryFile(mode='w+t') as f:
            json.dump(configuration, f)
            with self.assertRaises(ValueError):
                from_configuration_data(f.name, configuration)

    def test__target_type_missing(self):
        with open('%s/backuppy.json' % CONFIGURATION_PATH) as f:
            configuration = json.load(f)
        del configuration['target']['type']
        with NamedTemporaryFile(mode='w+t') as f:
            json.dump(configuration, f)
            with self.assertRaises(ValueError):
                from_configuration_data(f.name, configuration)

    @patch('logging.config.dictConfig')
    def test_logging(self, m):
        with open('%s/backuppy.json' % CONFIGURATION_PATH) as f:
            configuration_data = json.load(f)
            configuration_data['logging'] = {
                'version': 1,
                'handlers': {
                    __name__: {
                        'class': 'logging.FileHandler',
                        'filename': '/tmp/foo',
                    },
                },
                'loggers': {
                    'backuppy': {
                        'handlers': [__name__],
                    },
                },
            }
        from_configuration_data(f.name, configuration_data)
        m.assert_called_with(configuration_data['logging'])


class FromJsonTest(TestCase):
    def test_from_json(self):
        with open('%s/backuppy.json' % CONFIGURATION_PATH) as f:
            configuration = from_json(f)
        self.assertTrue(configuration.verbose)


class FromYamlTest(TestCase):
    def test_from_Yaml(self):
        with open('%s/backuppy.yml' % CONFIGURATION_PATH) as f:
            configuration = from_yaml(f)
        self.assertTrue(configuration.verbose)
