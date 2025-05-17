import os
import sys
import importlib
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from infrastructure import config as config_module

class TestConfig(unittest.TestCase):
    def test_default_elasticsearch_host(self):
        self.assertEqual(config_module.settings.ELASTICSEARCH_HOST, 'elasticsearch')

    def test_environment_override(self):
        os.environ['ELASTICSEARCH_HOST'] = 'example'
        importlib.reload(config_module)
        try:
            self.assertEqual(config_module.settings.ELASTICSEARCH_HOST, 'example')
        finally:
            os.environ.pop('ELASTICSEARCH_HOST')
            importlib.reload(config_module)

if __name__ == '__main__':
    unittest.main()
