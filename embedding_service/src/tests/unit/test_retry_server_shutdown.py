import os
import sys
import unittest
from unittest.mock import AsyncMock, patch, ANY

root_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, root_path)

from application.retry import retry_connection
from application.server_runner import run_api_server
from application.shutdown import shutdown


class TestRetryConnection(unittest.IsolatedAsyncioTestCase):
    async def test_retry_connection_retries_and_raises(self):
        calls = []

        async def connect():
            calls.append(1)
            raise RuntimeError("fail")

        with patch("application.retry.asyncio.sleep", new=AsyncMock()) as sleep_mock:
            with self.assertRaises(ConnectionError):
                await retry_connection(connect, max_retries=3, delay=0, name="svc")

        self.assertEqual(len(calls), 3)
        self.assertEqual(sleep_mock.await_count, 2)


class TestServerRunner(unittest.IsolatedAsyncioTestCase):
    async def test_run_api_server_invokes_uvicorn(self):
        with patch("application.server_runner.uvicorn.Server") as server_cls, patch(
            "application.server_runner.uvicorn.Config"
        ) as config_cls:
            server = AsyncMock()
            server_cls.return_value = server
            await run_api_server("127.0.0.1", 9999)
            config_cls.assert_called_once_with(
                ANY, host="127.0.0.1", port=9999, log_level="info"
            )
            server.serve.assert_awaited_once()


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
