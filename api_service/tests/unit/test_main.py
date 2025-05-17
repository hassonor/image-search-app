import os
import sys
import types
import importlib
import unittest
from unittest.mock import AsyncMock, MagicMock

root_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
sys.path.insert(0, os.path.abspath(root_path))


class TestMain(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        es_module = types.ModuleType('infrastructure.elasticsearch_client')
        es_module.elasticsearch_client = types.SimpleNamespace(
            es=types.SimpleNamespace(ping=AsyncMock()),
            close=AsyncMock()
        )
        sys.modules['infrastructure.elasticsearch_client'] = es_module

        metrics_module = types.ModuleType('infrastructure.metrics')
        metrics_module.start_metrics_server = MagicMock()
        sys.modules['infrastructure.metrics'] = metrics_module

        config_module = types.ModuleType('infrastructure.config')
        config_module.settings = types.SimpleNamespace(METRICS_PORT=9876)
        sys.modules['infrastructure.config'] = config_module

        logger_module = types.ModuleType('infrastructure.logging_config')
        logger_module.logger = MagicMock()
        sys.modules['infrastructure.logging_config'] = logger_module

        import main as main_module
        importlib.reload(main_module)
        self.main = main_module
        self.es = es_module.elasticsearch_client
        self.metrics = metrics_module

    async def test_startup_and_shutdown(self):
        await self.main.startup_event()
        self.es.es.ping.assert_awaited_once()
        self.metrics.start_metrics_server.assert_called_once_with(port=9876)

        await self.main.shutdown_event()
        self.es.close.assert_awaited_once()


if __name__ == '__main__':
    unittest.main()
