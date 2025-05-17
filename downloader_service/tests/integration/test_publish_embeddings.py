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

from application.messaging.publishers import publish_embeddings

class TestPublishEmbeddingsIntegration(unittest.IsolatedAsyncioTestCase):
    async def test_publish_embeddings(self):
        with patch(
            "application.messaging.publishers.rabbitmq_client.publish",
            new_callable=AsyncMock,
        ) as mock_publish:
            await publish_embeddings(1, "http://example.com/a.jpg", "/tmp/a.jpg")
            mock_publish.assert_awaited_once()
