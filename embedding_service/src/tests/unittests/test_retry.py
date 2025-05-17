import os
import sys
import unittest
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from application.retry import retry_connection

class TestRetryConnection(unittest.IsolatedAsyncioTestCase):
    async def test_retry_success(self):
        called = []
        async def connect():
            called.append(1)
        await retry_connection(connect, max_retries=3, delay=0.01, name='svc')
        self.assertEqual(len(called), 1)

    async def test_retry_failure(self):
        async def connect():
            raise Exception('fail')
        with self.assertRaises(ConnectionError):
            await retry_connection(connect, max_retries=2, delay=0.01, name='svc')

if __name__ == '__main__':
    unittest.main()
