import unittest
import os
import sys
import types
from unittest.mock import patch, AsyncMock

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

aio_pika_stub = types.ModuleType("aio_pika")
sys.modules.setdefault("aio_pika", aio_pika_stub)
sys.modules.setdefault("redis", types.ModuleType("redis"))
sys.modules.setdefault("redis.asyncio", types.ModuleType("redis.asyncio"))
from application.messaging.publishers import publish_embeddings
from application.messaging.callbacks import message_callback

class TestPublishers(unittest.IsolatedAsyncioTestCase):
    async def test_publish_embeddings(self):
        """Test that publish_embeddings publishes the correct message to the embedding queue."""
        with patch(
            "application.messaging.publishers.rabbitmq_client.publish",
            new_callable=AsyncMock,
        ) as mock_publish:
            await publish_embeddings(123, "http://example.com/img.jpg", "/local/path.jpg")
            mock_publish.assert_awaited_once()

    async def test_message_callback(self):
        """Test message_callback logic integrated with publish_embeddings mock."""
        mock_downloader = AsyncMock()
        mock_downloader.download_image = AsyncMock(return_value=(123, "/path/to/image.jpg"))

        # Patch publish_embeddings in callbacks
        with patch(
            "application.messaging.callbacks.publish_embeddings",
            new_callable=AsyncMock,
        ) as mock_publish:
            url = "http://example.com/image.jpg"
            await message_callback(url, mock_downloader)
            mock_downloader.download_image.assert_awaited_once_with(url)
            mock_publish.assert_awaited_once_with(123, url, "/path/to/image.jpg")
