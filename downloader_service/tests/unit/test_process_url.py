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

from application.messaging.callbacks import process_url


class TestProcessUrl(unittest.IsolatedAsyncioTestCase):
    async def test_process_url_publishes_on_success(self):
        downloader = AsyncMock()
        downloader.download_image = AsyncMock(return_value=(1, "/tmp/img.jpg"))
        with patch(
            "application.messaging.callbacks.publish_embeddings",
            new_callable=AsyncMock,
        ) as mock_publish:
            url = "http://example.com/img.jpg"
            await process_url(url, downloader)
            downloader.download_image.assert_awaited_once_with(url)
            mock_publish.assert_awaited_once_with(1, url, "/tmp/img.jpg")

    async def test_process_url_no_publish_when_none(self):
        downloader = AsyncMock()
        downloader.download_image = AsyncMock(return_value=None)
        with patch(
            "application.messaging.callbacks.publish_embeddings",
            new_callable=AsyncMock,
        ) as mock_publish:
            await process_url("http://example.com/x.jpg", downloader)
            mock_publish.assert_not_awaited()
