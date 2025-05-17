import json
import os
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

aio_pika_mod = types.ModuleType("aio_pika")


class DummyMsg:
    def __init__(self, body=b""):
        self.body = body


aio_pika_mod.Message = DummyMsg
aio_pika_mod.IncomingMessage = DummyMsg
sys.modules["aio_pika"] = aio_pika_mod
sys.modules.setdefault("redis", types.ModuleType("redis"))
sys.modules.setdefault("redis.asyncio", types.ModuleType("redis.asyncio"))

from infrastructure import rabbitmq_client as rabbitmq_client_module
from infrastructure.rabbitmq_client import RabbitMQClient

rabbitmq_client_module.aio_pika.Message = DummyMsg
rabbitmq_client_module.aio_pika.IncomingMessage = DummyMsg


class FakeMessage:
    def __init__(self, body):
        self.body = body

    class _CM:
        async def __aenter__(self):
            return None

        async def __aexit__(self, exc_type, exc, tb):
            pass

    def process(self):
        return self._CM()


class TestRabbitMQClient(unittest.IsolatedAsyncioTestCase):
    async def test_create_on_message(self):
        client = RabbitMQClient()
        callback = AsyncMock()
        on_message = client._create_on_message(callback)

        data = json.dumps({"url": "http://example.com"}).encode()
        msg = FakeMessage(data)
        await on_message(msg)
        callback.assert_awaited_once_with("http://example.com")

    async def test_publish_and_consume(self):
        client = RabbitMQClient()
        client.channel = AsyncMock()
        queue = AsyncMock()
        client.channel.declare_queue = AsyncMock(return_value=queue)
        queue.consume = AsyncMock()
        client.channel.default_exchange.publish = AsyncMock()

        await client.publish("q", "msg")
        client.channel.declare_queue.assert_called_with("q", durable=True)
        client.channel.default_exchange.publish.assert_awaited()

        await client.consume("q", AsyncMock())
        queue.consume.assert_awaited()

    async def test_on_message_bad_payload(self):
        client = RabbitMQClient()
        callback = AsyncMock()
        on_message = client._create_on_message(callback)

        bad_json = FakeMessage(b"not-json")
        await on_message(bad_json)
        callback.assert_not_called()

        missing_url = FakeMessage(json.dumps({"no": "url"}).encode())
        await on_message(missing_url)
        callback.assert_not_called()
