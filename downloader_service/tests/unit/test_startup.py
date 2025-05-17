import unittest
import os
import sys
import types
from unittest.mock import AsyncMock

root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

sys.modules.setdefault("redis", types.ModuleType("redis"))
sys.modules.setdefault("redis.asyncio", types.ModuleType("redis.asyncio"))
from application.retry import retry_connection

class TestRetryConnection(unittest.IsolatedAsyncioTestCase):
    async def test_retry_connection_success(self):
        """Test successful connection on the first try with retry_connection."""
        mock_connect = AsyncMock()
        await retry_connection(mock_connect, max_retries=2, delay=0.1, name="TestService")
        mock_connect.assert_awaited_once()

    async def test_retry_connection_failure(self):
        """Test that retry_connection raises ConnectionError after max_retries failures."""
        mock_connect = AsyncMock(side_effect=Exception("Connection failed"))
        with self.assertRaises(ConnectionError):
            await retry_connection(mock_connect, max_retries=2, delay=0.1, name="FailService")
        self.assertEqual(mock_connect.await_count, 2)
