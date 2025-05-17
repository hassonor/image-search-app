import sys
import os
import unittest
from unittest.mock import AsyncMock, patch
import types
from file_reader_service.tests.utils import setup_stub_modules

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)
setup_stub_modules()

# Stub infrastructure.redis_client so domain import succeeds
redis_stub = types.ModuleType("infrastructure.redis_client")
class RedisClient:
    async def connect(self):
        pass
redis_stub.redis_client = AsyncMock()
redis_stub.RedisClient = RedisClient
sys.modules.setdefault("infrastructure.redis_client", redis_stub)

from interface.api import health_check, run_api_server
import importlib
import domain.file_reader_service as fr_module
importlib.reload(fr_module)
from domain.file_reader_service import FileReaderService


class DummyRedis:
    async def check_urls_batch(self, urls):
        return urls


class TestAPI(unittest.IsolatedAsyncioTestCase):
    async def test_health_check(self):
        self.assertEqual(
            await health_check(),
            {"status": "ok", "service": "file_reader_service"},
        )

    async def test_run_api_server(self):
        server = AsyncMock()
        uvicorn_stub = types.ModuleType("uvicorn")
        uvicorn_stub.Config = lambda *a, **k: None
        uvicorn_stub.Server = lambda cfg: server
        with patch.dict(sys.modules, {"uvicorn": uvicorn_stub}):
            await run_api_server("0.0.0.0", 1234)
        server.serve.assert_awaited_once()


class TestDomain(unittest.IsolatedAsyncioTestCase):
    async def test_filter_new_urls(self):
        service = FileReaderService(redis_client=DummyRedis())
        result1 = await service.filter_new_urls(["a", "b"])
        self.assertEqual(set(result1), {"a", "b"})

        result2 = await service.filter_new_urls(["a"])
        self.assertEqual(result2, [])
