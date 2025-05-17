import sys
import os
import types
import unittest
from unittest.mock import AsyncMock, patch
from file_reader_service.tests.utils import setup_stub_modules

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)
setup_stub_modules()



class DummyConnection:
    def __init__(self):
        self.closed = False

    async def channel(self):
        return AsyncMock()

    async def close(self):
        self.closed = True


class DummyPipeline:
    def __init__(self):
        self.calls = []

    def exists(self, key):
        self.calls.append(key)

    async def execute(self):
        results = [0] * len(self.calls)
        self.calls.clear()
        return results


class DummyRedis:
    def __init__(self):
        self.closed = False
        self.pipe = DummyPipeline()

    async def ping(self):
        return True

    def pipeline(self):
        return self.pipe

    async def close(self):
        self.closed = True


class TestRabbitMQClient(unittest.IsolatedAsyncioTestCase):
    async def test_connect_and_close(self):
        if "infrastructure.rabbitmq_client" in sys.modules:
            del sys.modules["infrastructure.rabbitmq_client"]
        import importlib
        RabbitMQ = importlib.import_module("infrastructure.rabbitmq_client")
        RabbitMQClient = RabbitMQ.RabbitMQClient
        dummy_conn = DummyConnection()
        with patch("infrastructure.rabbitmq_client.aio_pika.connect_robust", AsyncMock(return_value=dummy_conn)):
            client = RabbitMQClient()
            await client.connect()
            self.assertIs(client.connection, dummy_conn)
            self.assertIsNotNone(client.channel)
            await client.close()
        self.assertTrue(dummy_conn.closed)


class TestRedisClient(unittest.IsolatedAsyncioTestCase):
    async def test_full_flow(self):
        if "infrastructure.redis_client" in sys.modules:
            del sys.modules["infrastructure.redis_client"]
        import importlib
        RedisMod = importlib.import_module("infrastructure.redis_client")
        RedisClient = RedisMod.RedisClient
        dummy = DummyRedis()
        with patch("infrastructure.redis_client.redis.Redis", return_value=dummy):
            client = RedisClient()
            await client.connect()
            result = await client.check_urls_batch(["a", "b"])
            self.assertEqual(result, ["a", "b"])
            await client.close()
        self.assertTrue(dummy.closed)
