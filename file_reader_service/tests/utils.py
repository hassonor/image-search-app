import sys
import types
from types import SimpleNamespace
from unittest.mock import AsyncMock


class _Value:
    def __init__(self) -> None:
        self.val = 0.0

    def get(self) -> float:
        return self.val


class Counter:
    def __init__(self, *_, **__):
        self._value = _Value()

    def inc(self, amount: float = 1.0) -> None:
        self._value.val += amount


class Histogram:
    def __init__(self, *_, **__):
        self._value = _Value()

    def observe(self, value: float) -> None:  # noqa: ARG002
        self._value.val += 1


def setup_stub_modules():
    """Install stub modules for optional dependencies."""
    aiofiles_stub = types.ModuleType("aiofiles")
    aiofiles_stub.open = lambda *args, **kwargs: None
    sys.modules["aiofiles"] = aiofiles_stub

    aio_pika_stub = types.ModuleType("aio_pika")

    class Message:
        def __init__(self, body):
            self.body = body

    aio_pika_stub.Message = Message

    async def _connect_robust(*args, **kwargs):
        return SimpleNamespace(channel=lambda: AsyncMock())

    aio_pika_stub.connect_robust = _connect_robust
    sys.modules["aio_pika"] = aio_pika_stub

    redis_mod = types.ModuleType("redis.asyncio")

    class DummyRedis:
        def __init__(self, *args, **kwargs):
            pass

    redis_mod.Redis = DummyRedis
    sys.modules["redis.asyncio"] = redis_mod
    sys.modules["redis"] = types.ModuleType("redis")

    pybloom_stub = types.ModuleType("pybloom_live")

    class BloomFilter:
        def __init__(self, *args, **kwargs):
            self._items = set()

        def add(self, item):
            self._items.add(item)

        def __contains__(self, item):
            return item in self._items

    pybloom_stub.BloomFilter = BloomFilter
    sys.modules["pybloom_live"] = pybloom_stub

    prom_stub = types.ModuleType("prometheus_client")
    prom_stub.Counter = Counter
    prom_stub.Histogram = Histogram
    prom_stub.start_http_server = lambda *args, **kwargs: None
    sys.modules["prometheus_client"] = prom_stub

    uvicorn_stub = types.ModuleType("uvicorn")
    uvicorn_stub.Config = lambda *a, **k: None

    class Server:
        async def serve(self):
            return None

    uvicorn_stub.Server = lambda *a, **k: Server()
    sys.modules["uvicorn"] = uvicorn_stub
