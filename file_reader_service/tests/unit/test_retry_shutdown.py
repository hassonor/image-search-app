import sys
import os
import types
import unittest
from unittest.mock import AsyncMock, patch
from file_reader_service.tests.utils import setup_stub_modules

# Ensure src is importable
root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)
setup_stub_modules()

from application.retry import retry_connection
from application.shutdown import shutdown


class TestRetry(unittest.IsolatedAsyncioTestCase):
    async def test_retry_success_after_failures(self):
        calls = []

        async def connect():
            calls.append(1)
            if len(calls) < 3:
                raise RuntimeError("fail")

        with patch("application.retry.asyncio.sleep", new=AsyncMock()):
            await retry_connection(connect, max_retries=3, delay=0, name="svc")
        self.assertEqual(len(calls), 3)

    async def test_retry_failure(self):
        async def connect():
            raise RuntimeError("boom")

        with patch("application.retry.asyncio.sleep", new=AsyncMock()):
            with self.assertRaises(ConnectionError):
                await retry_connection(connect, max_retries=2, delay=0, name="svc")


class DummyTask:
    def __init__(self):
        self.canceled = False

    def cancel(self):
        self.canceled = True


class TestShutdown(unittest.TestCase):
    def test_shutdown_cancels_tasks(self):
        t1 = DummyTask()
        t2 = DummyTask()
        with patch("application.shutdown.asyncio.all_tasks", return_value=[t1, t2]):
            shutdown()
        self.assertTrue(t1.canceled and t2.canceled)
