import os
import sys
import types
import unittest
from unittest.mock import AsyncMock, MagicMock, mock_open, patch

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

# Stub external modules that may not be installed
sys.modules.setdefault("aio_pika", types.ModuleType("aio_pika"))
redis_mod = types.ModuleType("redis")
redis_async_mod = types.ModuleType("redis.asyncio")


class DummyRedis:
    def __init__(self, *args, **kwargs):
        pass

    def pipeline(self):
        return AsyncMock()


redis_async_mod.Redis = DummyRedis
sys.modules["redis"] = redis_mod
sys.modules["redis.asyncio"] = redis_async_mod
aiohttp_mod = types.ModuleType("aiohttp")
aiohttp_mod.ClientSession = AsyncMock


class DummyError(Exception):
    pass


aiohttp_mod.ClientConnectorError = DummyError
aiohttp_mod.ClientResponseError = DummyError
aiohttp_mod.ClientError = DummyError
sys.modules.setdefault("aiohttp", aiohttp_mod)
pybloom_mod = types.ModuleType("pybloom_live")


class DummyBloom:
    def __init__(self, *a, **k):
        self.set = set()

    def __contains__(self, item):
        return item in self.set

    def add(self, item):
        self.set.add(item)


pybloom_mod.BloomFilter = DummyBloom
sys.modules.setdefault("pybloom_live", pybloom_mod)
prom_mod = types.ModuleType("prometheus_client")
prom_mod.Counter = lambda *a, **k: None
prom_mod.Histogram = lambda *a, **k: None
prom_mod.start_http_server = lambda *a, **k: None
sys.modules.setdefault("prometheus_client", prom_mod)
asyncpg_mod = types.ModuleType("asyncpg")
asyncpg_mod.create_pool = AsyncMock()
sys.modules.setdefault("asyncpg", asyncpg_mod)

from domain.download_service import DownloaderService


class MockResponse:
    def __init__(self, status=200, data=b"data"):
        self.status = status
        self._data = data

    async def read(self):
        return self._data

    def raise_for_status(self):
        if self.status >= 400:
            from aiohttp import ClientResponseError

            raise ClientResponseError(
                request_info=None, history=(), status=self.status, message="error"
            )

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass


class TestDownloaderService(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.mock_db = AsyncMock()
        self.mock_redis = AsyncMock()
        patcher = patch("domain.download_service.aiohttp.ClientSession")
        self.addCleanup(patcher.stop)
        self.mock_session_cls = patcher.start()
        self.mock_session = self.mock_session_cls.return_value
        self.service = DownloaderService(database=self.mock_db, redis_client=self.mock_redis)
        self.service.session = self.mock_session

    async def test_download_image_success(self):
        self.mock_redis.acquire_download_lock.return_value = True
        self.mock_redis.is_url_downloaded.return_value = False
        self.mock_redis.is_url_marked_as_not_found.return_value = False
        self.mock_db.store_image_record = AsyncMock(return_value=123)
        self.mock_session.get.return_value = MockResponse(200, b"abc")

        with (
            patch("domain.download_service.os.makedirs"),
            patch("builtins.open", mock_open()),
            patch("domain.download_service.images_downloaded") as mock_counter,
            patch("domain.download_service.download_latency") as mock_latency,
        ):
            result = await self.service.download_image("http://example.com/a.jpg")
            self.assertEqual(result[0], 123)
            self.assertTrue(result[1].endswith(".jpg"))
            mock_counter.inc.assert_called_once()
            mock_latency.observe.assert_called_once()

    async def test_download_image_invalid_url(self):
        self.mock_redis.acquire_download_lock.return_value = True
        with (
            patch.object(DownloaderService, "is_valid_url", return_value=False),
            patch("domain.download_service.download_errors") as mock_errors,
        ):
            result = await self.service.download_image("bad-url")
            self.assertIsNone(result)
            mock_errors.inc.assert_called_once()

    async def test_download_image_404(self):
        self.mock_redis.acquire_download_lock.return_value = True
        self.mock_redis.is_url_downloaded.return_value = False
        self.mock_redis.is_url_marked_as_not_found.return_value = False
        self.mock_session.get.return_value = MockResponse(404)
        self.mock_redis.cache_url_as_not_found = AsyncMock()
        with (
            patch("domain.download_service.download_errors") as mock_errors,
            patch("domain.download_service.download_latency"),
            patch("domain.download_service.images_downloaded"),
        ):
            result = await self.service.download_image("http://example.com/missing.jpg")
            self.assertIsNone(result)
            mock_errors.inc.assert_not_called()

    def test_generate_filename(self):
        name = DownloaderService.generate_filename("http://example.com/img.png")
        self.assertTrue(name.endswith(".png"))
        self.assertEqual(len(name.split(".")[0]), 64)

    def test_is_valid_url(self):
        self.assertTrue(DownloaderService.is_valid_url("http://example.com"))
        self.assertFalse(DownloaderService.is_valid_url("not-a-url"))
