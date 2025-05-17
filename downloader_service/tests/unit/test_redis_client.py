import os
import sys
import types
import unittest
from unittest.mock import AsyncMock

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

sys.modules.setdefault("aio_pika", types.ModuleType("aio_pika"))
redis_mod = types.ModuleType("redis")
redis_async_mod = types.ModuleType("redis.asyncio")


class DummyRedis:
    def __init__(self, *args, **kwargs):
        pass

    def pipeline(self):
        return AsyncMock()


redis_async_mod.Redis = DummyRedis
sys.modules["redis"] = redis_mod
sys.modules["redis.asyncio"] = redis_async_mod

from infrastructure.redis_client import RedisClient


class FakePipeline:
    def __init__(self, results):
        self.results = results
        self.calls = []

    def exists(self, key):
        self.calls.append(key)
        return self

    async def execute(self):
        return self.results


class TestRedisClient(unittest.IsolatedAsyncioTestCase):
    async def test_check_urls_batch(self):
        client = RedisClient()
        results_iter = iter([[0, 1, 0], [0, 0, 1]])

        def pipeline_side_effect():
            return FakePipeline(next(results_iter))

        redis_mock = types.SimpleNamespace(pipeline=pipeline_side_effect)
        client.redis = redis_mock

        urls = ["a", "b", "c"]
        remaining = await client.check_urls_batch(urls)
        self.assertEqual(remaining, ["a"])
