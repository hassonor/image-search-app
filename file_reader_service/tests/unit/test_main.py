import os
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch
from file_reader_service.tests.utils import setup_stub_modules

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)
setup_stub_modules()


class DummyEvent:
    async def wait(self):
        return None


class TestMain(unittest.IsolatedAsyncioTestCase):
    async def test_main_async(self):
        config_stub = types.ModuleType("infrastructure.config")
        config_stub.settings = types.SimpleNamespace(
            METRICS_PORT=0,
            API_PORT=0,
            URLS_FILE_PATH="urls.txt",
            URL_CHUNK_SIZE=1,
            LOG_LEVEL="INFO",
            LOG_FORMAT="%(message)s",
        )

        rabbitmq_stub = types.ModuleType("infrastructure.rabbitmq_client")
        rabbitmq_stub.rabbitmq_client = AsyncMock()

        redis_stub = types.ModuleType("infrastructure.redis_client")
        redis_stub.redis_client = AsyncMock()
        redis_stub.redis_client.connect = AsyncMock()
        redis_stub.redis_client.close = AsyncMock()

        modules = {
            "infrastructure.config": config_stub,
            "infrastructure.rabbitmq_client": rabbitmq_stub,
            "infrastructure.redis_client": redis_stub,
        }

        with patch.dict(sys.modules, modules):
            from main import main_async
            with patch("main.retry_connection", AsyncMock()), patch(
                "main.publish_urls", AsyncMock()
            ), patch("main.start_metrics_server"), patch(
                "main.run_api_server", AsyncMock()
            ), patch("main.asyncio.Event", return_value=DummyEvent()):
                await main_async()
            rabbitmq_stub.rabbitmq_client.close.assert_awaited_once()
            redis_stub.redis_client.close.assert_awaited_once()
