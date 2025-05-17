import os
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

# Ensure src directory is on path
root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

# Stub optional external modules
sys.modules.setdefault("redis", types.ModuleType("redis"))
sys.modules.setdefault("redis.asyncio", types.ModuleType("redis.asyncio"))

import main  # noqa: E402


class DummyEvent:
    def __init__(self):
        self.wait = AsyncMock()


class TestMainAsync(unittest.IsolatedAsyncioTestCase):
    async def test_main_async_runs_all_steps(self):
        retry_names = []

        async def fake_retry(coro, *a, name=None, **k):
            retry_names.append(name)
            await coro()

        with patch.object(main, "DownloaderService") as Service, \
            patch.object(main, "database") as db, \
            patch.object(main, "redis_client") as redis, \
            patch.object(main, "rabbitmq_client") as rabbit, \
            patch.object(main, "retry_connection", side_effect=fake_retry), \
            patch.object(main, "start_metrics_server") as metrics, \
            patch.object(main, "run_api_server", new=AsyncMock()) as api_server, \
            patch.object(main.asyncio, "Event", return_value=DummyEvent()):

            db.connect = AsyncMock()
            db.close = AsyncMock()
            redis.connect = AsyncMock()
            redis.close = AsyncMock()
            rabbit.connect = AsyncMock()
            rabbit.consume = AsyncMock()
            rabbit.close = AsyncMock()
            instance = Service.return_value
            instance.close = AsyncMock()

            await main.main_async()

            self.assertEqual(
                retry_names,
                ["PostgreSQL", "Redis", "RabbitMQ", "RabbitMQ Consumer"],
            )
            metrics.assert_called_once_with(port=main.settings.METRICS_PORT)
            api_server.assert_called_once()
            instance.close.assert_awaited_once()
            rabbit.close.assert_awaited_once()
            redis.close.assert_awaited_once()
            db.close.assert_awaited_once()
