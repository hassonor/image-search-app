import os
import sys
import types
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Stub missing external packages
sys.modules['aiohttp'] = types.ModuleType('aiohttp')
sys.modules['pybloom_live'] = types.ModuleType('pybloom_live')
sys.modules['pybloom_live'].BloomFilter = lambda *a, **k: None
sys.modules['asyncpg'] = types.ModuleType('asyncpg')
sys.modules['infrastructure.database'] = types.ModuleType('infrastructure.database')
sys.modules['infrastructure.database'].Database = object
sys.modules['infrastructure.redis_client'] = types.ModuleType('infrastructure.redis_client')
sys.modules['infrastructure.redis_client'].RedisClient = object
metrics_mod = types.ModuleType('infrastructure.metrics')
metrics_mod.download_errors = object()
metrics_mod.download_latency = object()
metrics_mod.images_downloaded = object()
sys.modules['infrastructure.metrics'] = metrics_mod

from domain.download_service import DownloaderService

class TestDownloaderUtils(unittest.TestCase):
    def test_is_valid_url(self):
        self.assertTrue(DownloaderService.is_valid_url('http://example.com'))
        self.assertFalse(DownloaderService.is_valid_url('ftp://example.com'))
        self.assertFalse(DownloaderService.is_valid_url('invalid'))

    def test_generate_filename_extension(self):
        name1 = DownloaderService.generate_filename('http://example.com/a.png')
        name2 = DownloaderService.generate_filename('http://example.com/a.png')
        self.assertTrue(name1.endswith('.png'))
        self.assertEqual(name1, name2)

if __name__ == '__main__':
    unittest.main()
