import os
import sys
import types
import unittest
from unittest.mock import patch

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

sys.modules.setdefault("aio_pika", types.ModuleType("aio_pika"))
sys.modules.setdefault("redis", types.ModuleType("redis"))
sys.modules.setdefault("redis.asyncio", types.ModuleType("redis.asyncio"))

from infrastructure.logging_config import setup_logging


class TestLoggingConfig(unittest.TestCase):
    def test_setup_logging_returns_logger(self):
        with (
            patch("logging.basicConfig") as basic_config,
            patch("logging.getLogger") as get_logger,
        ):
            logger_instance = get_logger.return_value
            logger = setup_logging()
            basic_config.assert_called_once()
            get_logger.assert_called_once_with("downloader_service")
            self.assertIs(logger, logger_instance)
