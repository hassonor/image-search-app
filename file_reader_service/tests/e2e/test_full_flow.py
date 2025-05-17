import unittest
import sys
import os
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

from file_reader_service.src.application.publisher import process_and_publish_chunk
from domain.file_reader_service import FileReaderService

class TestFileReaderE2E(unittest.IsolatedAsyncioTestCase):
    async def test_full_flow(self):
        mock_channel = AsyncMock()
        with patch(
            "file_reader_service.src.application.publisher.rabbitmq_client.channel",
            mock_channel,
        ):
            mock_redis_client = AsyncMock()
            mock_redis_client.check_urls_batch.return_value = [
                "http://example.com/img.jpg"
            ]
            service = FileReaderService(redis_client=mock_redis_client)
            await process_and_publish_chunk(["http://example.com/img.jpg"], service)
        self.assertEqual(mock_channel.default_exchange.publish.await_count, 1)
