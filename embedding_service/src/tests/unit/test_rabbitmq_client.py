import contextlib
import json
import os
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

root_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, root_path)

aio_pika_stub = types.ModuleType("aio_pika")


class IncomingMessage:  # minimal stub for type hints
    pass


aio_pika_stub.IncomingMessage = IncomingMessage
sys.modules.setdefault("aio_pika", aio_pika_stub)


class DummyProcess:
    async def __aenter__(self):
        return None

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummyMessage:
    def __init__(self, body: str):
        self.body = body.encode()

    def process(self):
        return DummyProcess()


class TestCreateOnMessage(unittest.IsolatedAsyncioTestCase):
    async def test_valid_message(self):
        from infrastructure.rabbitmq_client import RabbitMQClient

        client = RabbitMQClient()
        callback = AsyncMock()
        on_message = client._create_on_message(callback)
        msg = DummyMessage(json.dumps({"image_id": 1, "image_url": "url"}))
        with patch("infrastructure.rabbitmq_client.logger") as mock_logger:
            await on_message(msg)
            callback.assert_awaited_once_with({"image_id": 1, "image_url": "url"})
            mock_logger.debug.assert_called_once()
            mock_logger.info.assert_called_once_with("Processed image_id: %s", 1)

    async def test_invalid_message(self):
        from infrastructure.rabbitmq_client import RabbitMQClient

        client = RabbitMQClient()
        callback = AsyncMock()
        on_message = client._create_on_message(callback)
        msg = DummyMessage(json.dumps({"other": "x"}))
        with patch("infrastructure.rabbitmq_client.logger") as mock_logger:
            await on_message(msg)
            callback.assert_not_awaited()
            mock_logger.warning.assert_called_once()

    async def test_callback_exception_logged(self):
        from infrastructure.rabbitmq_client import RabbitMQClient

        client = RabbitMQClient()
        callback = AsyncMock(side_effect=RuntimeError("boom"))
        on_message = client._create_on_message(callback)
        msg = DummyMessage(json.dumps({"image_id": 1, "image_url": "url"}))
        with patch("infrastructure.rabbitmq_client.logger") as mock_logger:
            await on_message(msg)
            mock_logger.exception.assert_called_once()
