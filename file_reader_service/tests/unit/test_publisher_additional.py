import os
import sys
import unittest
from unittest.mock import AsyncMock, patch
import types
from file_reader_service.tests.utils import setup_stub_modules

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)
setup_stub_modules()

redis_stub = types.ModuleType("infrastructure.redis_client")
class RedisClient:
    async def connect(self):
        pass
redis_stub.redis_client = AsyncMock()
redis_stub.RedisClient = RedisClient
sys.modules.setdefault("infrastructure.redis_client", redis_stub)

from application.publisher import publish_urls, process_and_publish_chunk
from domain.file_reader_service import FileReaderService


class DummyService(FileReaderService):
    def __init__(self):
        super().__init__(redis_client=AsyncMock())
        self.redis_client.check_urls_batch.side_effect = lambda urls: urls


class TestPublisherAdditional(unittest.IsolatedAsyncioTestCase):
    async def test_publish_urls_file_not_found(self):
        service = DummyService()
        await publish_urls("/nonexistent/file.txt", 1, service)

    async def test_publish_urls_and_empty_chunk(self):
        service = DummyService()

        def async_open(path, mode):
            class AF:
                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc, tb):
                    pass

                async def __aiter__(self):
                    yield ""
                    yield "#comment"
                    yield "http://example.com"

            return AF()

        mock_channel = AsyncMock()
        mock_channel.default_exchange.publish = AsyncMock()
        with patch("application.publisher.aiofiles.open", async_open), patch(
            "application.publisher.rabbitmq_client.channel", mock_channel
        ), patch("application.publisher.os.path.exists", return_value=True):
            await publish_urls("dummy", 10, service)
        mock_channel.default_exchange.publish.assert_awaited_once()

        await process_and_publish_chunk([], service)
