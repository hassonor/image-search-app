import unittest
import os
import sys
import types
from unittest.mock import AsyncMock, patch

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

aio_pika_stub = types.ModuleType("aio_pika")
sys.modules.setdefault("aio_pika", aio_pika_stub)
sys.modules.setdefault("redis", types.ModuleType("redis"))
sys.modules.setdefault("redis.asyncio", types.ModuleType("redis.asyncio"))

from application.messaging.callbacks import message_callback

class TestDownloaderE2E(unittest.IsolatedAsyncioTestCase):
    async def test_full_flow(self):
        mock_downloader = AsyncMock()
        mock_downloader.download_image = AsyncMock(return_value=(123, "/tmp/a.jpg"))

        with patch(
            "application.messaging.callbacks.publish_embeddings", new_callable=AsyncMock
        ) as mock_publish:
            await message_callback("http://example.com/a.jpg", mock_downloader)
            mock_downloader.download_image.assert_awaited_once_with("http://example.com/a.jpg")
            mock_publish.assert_awaited_once_with(123, "http://example.com/a.jpg", "/tmp/a.jpg")
