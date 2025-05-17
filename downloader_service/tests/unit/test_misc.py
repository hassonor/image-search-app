import os
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

sys.modules.setdefault("aio_pika", types.ModuleType("aio_pika"))
sys.modules.setdefault("redis", types.ModuleType("redis"))
sys.modules.setdefault("redis.asyncio", types.ModuleType("redis.asyncio"))
asyncpg_mod = types.ModuleType("asyncpg")
asyncpg_mod.create_pool = AsyncMock()
sys.modules.setdefault("asyncpg", asyncpg_mod)
prom_mod = types.ModuleType("prometheus_client")
prom_mod.Counter = lambda *a, **k: None
prom_mod.Histogram = lambda *a, **k: None
prom_mod.start_http_server = lambda *a, **k: None
sys.modules.setdefault("prometheus_client", prom_mod)

from application.server_runner import run_api_server
from application.shutdown import shutdown
from infrastructure.database import Database
from infrastructure.metrics import start_metrics_server
from interface.api import health_check


class TestMisc(unittest.IsolatedAsyncioTestCase):
    async def test_run_api_server(self):
        with patch("application.server_runner.uvicorn.Server") as server_cls:
            server = AsyncMock()
            server_cls.return_value = server
            await run_api_server("0.0.0.0", 1234)
            server.serve.assert_awaited_once()

    def test_shutdown(self):
        with patch("asyncio.all_tasks", return_value=[AsyncMock()]) as all_tasks:
            shutdown()
            all_tasks.assert_called_once()

    async def test_start_metrics_server(self):
        with patch("infrastructure.metrics.start_http_server") as start_http:
            start_metrics_server(port=9999)
            start_http.assert_called_once_with(9999)

    async def test_api_health_check(self):
        result = await health_check()
        self.assertEqual(result["status"], "ok")


class TestDatabase(unittest.IsolatedAsyncioTestCase):
    async def test_store_image_record(self):
        db = Database()
        db.pool = AsyncMock()
        conn = AsyncMock()

        class DummyAcquire:
            def __init__(self, c):
                self.c = c

            async def __aenter__(self):
                return self.c

            async def __aexit__(self, exc_type, exc, tb):
                return False

        db.pool.acquire = lambda: DummyAcquire(conn)

        conn.fetchrow = AsyncMock(side_effect=[{"id": 5}, None])
        result = await db.store_image_record("u", "/f")
        self.assertEqual(result, 5)

        conn.fetchrow = AsyncMock(side_effect=[None, {"id": 7}])
        result = await db.store_image_record("u2", "/f2")
        self.assertEqual(result, 7)

        conn.fetchrow = AsyncMock(side_effect=[None, None])
        result = await db.store_image_record("u3", "/f3")
        self.assertIsNone(result)
