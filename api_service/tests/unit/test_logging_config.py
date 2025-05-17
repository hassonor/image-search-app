import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from infrastructure.logging_config import setup_logging

class TestLoggingConfig(unittest.TestCase):
    def test_setup_logging_returns_logger(self):
        logger = setup_logging()
        self.assertTrue(logger.name)

if __name__ == '__main__':
    unittest.main()
