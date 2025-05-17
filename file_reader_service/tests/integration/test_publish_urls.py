import os
import tempfile
import unittest
import sys
import types
from unittest.mock import AsyncMock, patch

# Stub aiofiles so publisher module imports succeed
aiofiles_stub = types.ModuleType("aiofiles")
aiofiles_stub.open = lambda *args, **kwargs: None
sys.modules.setdefault("aiofiles", aiofiles_stub)
aio_pika_stub = types.ModuleType("aio_pika")
class Message:
    def __init__(self, body):
        self.body = body
aio_pika_stub.Message = Message
sys.modules.setdefault("aio_pika", aio_pika_stub)
sys.modules.setdefault("redis", types.ModuleType("redis"))
sys.modules.setdefault("redis.asyncio", types.ModuleType("redis.asyncio"))
pybloom_stub = types.ModuleType("pybloom_live")
class BloomFilter:
    def __init__(self, *args, **kwargs):
        pass

    def add(self, item):
        pass

    def __contains__(self, item):
        return False

pybloom_stub.BloomFilter = BloomFilter
sys.modules.setdefault("pybloom_live", pybloom_stub)
config_stub = types.ModuleType("infrastructure.config")
config_stub.settings = types.SimpleNamespace(
    DOWNLOAD_QUEUE="queue",
    BLOOM_EXPECTED_ITEMS=10,
    BLOOM_ERROR_RATE=0.001,
)
sys.modules.setdefault("infrastructure.config", config_stub)
rabbitmq_stub = types.ModuleType("infrastructure.rabbitmq_client")
rabbitmq_stub.rabbitmq_client = AsyncMock()
sys.modules.setdefault("infrastructure.rabbitmq_client", rabbitmq_stub)
redis_stub = types.ModuleType("infrastructure.redis_client")
class RedisClient:
    async def connect(self):
        pass
redis_stub.redis_client = AsyncMock()
redis_stub.RedisClient = RedisClient
sys.modules.setdefault("infrastructure.redis_client", redis_stub)

# Ensure service source is importable
root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

from file_reader_service.src.application.publisher import publish_urls
from domain.file_reader_service import FileReaderService

class TestPublishUrlsIntegration(unittest.IsolatedAsyncioTestCase):
    async def test_publish_urls(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tmp:
            tmp.write("http://example.com/a.jpg\n")
            tmp.write("http://example.com/b.jpg\n")
            file_path = tmp.name

        class AsyncFile:
            def __init__(self, path, mode):
                self._f = open(path, mode)

            async def __aenter__(self):
                return self

            async def __aexit__(self, exc_type, exc, tb):
                self._f.close()

            async def __aiter__(self):
                for line in self._f:
                    yield line

        mock_channel = AsyncMock()
        service = FileReaderService(redis_client=AsyncMock())
        service.redis_client.check_urls_batch.side_effect = lambda urls: urls

        with patch("file_reader_service.src.application.publisher.aiofiles.open", lambda p, m: AsyncFile(p, m)), \
             patch("file_reader_service.src.application.publisher.rabbitmq_client.channel", mock_channel):
            await publish_urls(file_path, 1, service)

        self.assertEqual(mock_channel.default_exchange.publish.await_count, 2)
        os.remove(file_path)
