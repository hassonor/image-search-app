import sys
import os
import importlib
import unittest
from unittest.mock import patch

# Ensure src path
root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

if "infrastructure.config" in sys.modules:
    del sys.modules["infrastructure.config"]
import importlib
config = importlib.import_module("infrastructure.config")
logging_config = importlib.import_module("infrastructure.logging_config")
metrics = importlib.import_module("infrastructure.metrics")


class TestInfrastructure(unittest.TestCase):
    def test_settings_defaults(self):
        importlib.reload(config)
        self.assertEqual(config.settings.RABBITMQ_HOST, "localhost")

    def test_setup_logging(self):
        importlib.reload(logging_config)
        with patch("logging.basicConfig") as basic:
            logger = logging_config.setup_logging()
        basic.assert_called_once()
        self.assertEqual(logger.name, "file_reader_service")

    def test_start_metrics_server(self):
        with patch("infrastructure.metrics.start_http_server") as start:
            metrics.start_metrics_server(port=1234)
            start.assert_called_once_with(1234)
