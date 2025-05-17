import os
import sys
import unittest
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from application.shutdown import shutdown

class TestShutdown(unittest.IsolatedAsyncioTestCase):
    async def test_shutdown_cancels_tasks(self):
        task = asyncio.create_task(asyncio.sleep(10))
        shutdown()
        try:
            await task
        except asyncio.CancelledError:
            pass
        self.assertTrue(task.cancelled())

if __name__ == '__main__':
    unittest.main()
