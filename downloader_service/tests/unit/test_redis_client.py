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


class SimpleRedis:
    def __init__(self):
        self.store = {}

    async def set(self, key, value, nx=False, ex=None):
        if nx and key in self.store:
            return None
        self.store[key] = value
        return True

    async def exists(self, key):
        return 1 if key in self.store else 0

    async def delete(self, key):
        self.store.pop(key, None)

    def pipeline(self):
        return AsyncMock()


class TestRedisClientLocks(unittest.IsolatedAsyncioTestCase):
    async def test_lock_and_flags(self):
        client = RedisClient()
        client.redis = SimpleRedis()

        acquired = await client.acquire_download_lock("u")
        self.assertTrue(acquired)
        self.assertFalse(await client.acquire_download_lock("u"))

        await client.cache_url_as_downloaded("u", "/p")
        self.assertTrue(await client.is_url_downloaded("u"))

        await client.cache_url_as_not_found(
            "nf",
        )
        self.assertTrue(await client.is_url_marked_as_not_found("nf"))

        await client.release_download_lock("u")
        self.assertEqual(await client.redis.exists("lock:u"), 0)
