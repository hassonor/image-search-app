"""
domain/file_reader_service.py

Handles filtering of URLs before publishing:
- Uses a Bloom filter for fast in-memory checks.
- Uses Redis to ensure the URL is truly new.
"""

import logging
from typing import List
from pybloom_live import BloomFilter
from infrastructure.config import settings
from infrastructure.redis_client import RedisClient

logger = logging.getLogger(__name__)

class FileReaderService:
    def __init__(self, redis_client: RedisClient):
        self.redis_client = redis_client
        # Initialize Bloom filter with similar parameters as downloader
        self.bloom = BloomFilter(
            capacity=settings.BLOOM_EXPECTED_ITEMS,
            error_rate=settings.BLOOM_ERROR_RATE
        )

    async def filter_new_urls(self, urls: List[str]) -> List[str]:
        """
        Check which URLs are new using bloom filter and Redis.
        - First skip any URL already in bloom.
        - For remaining URLs, check Redis.
        - Add newly discovered URLs to bloom to prevent re-checking.
        """
        candidate_urls = [url for url in urls if url not in self.bloom]
        if not candidate_urls:
            return []

        new_urls = await self.redis_client.check_urls_batch(candidate_urls)
        for url in new_urls:
            self.bloom.add(url)

        return new_urls
