"""
Redis client module for handling URL caching, distributed locks, and batch checks.

Handles:
- Check if a URL is already downloaded/not-found.
- Acquire and release a distributed lock per URL to avoid duplicates.
- Batch checking URLs to filter out already processed entries.
"""

import logging
import redis.asyncio as redis
from config import settings
from typing import List

logger = logging.getLogger(__name__)

class RedisClient:
    """Manages Redis caching and locking for URLs."""
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    async def connect(self) -> None:
        """Check connection by pinging Redis."""
        try:
            await self.redis.ping()
            logger.info("Connected to Redis.")
        except Exception as e:
            logger.exception("Failed to connect to Redis: %s", e)
            raise

    async def is_url_downloaded(self, url: str) -> bool:
        """Return True if the URL has already been downloaded."""
        key = f"downloaded:{url}"
        return (await self.redis.exists(key)) == 1

    async def cache_url_as_downloaded(self, url: str, file_path: str) -> None:
        """Mark the URL as downloaded by caching its file path."""
        key = f"downloaded:{url}"
        await self.redis.set(key, file_path)

    async def is_url_marked_as_not_found(self, url: str) -> bool:
        """Return True if the URL was previously marked as not found."""
        key = f"not_found:{url}"
        return (await self.redis.exists(key)) == 1

    async def cache_url_as_not_found(self, url: str) -> None:
        """Cache the URL as not found."""
        key = f"not_found:{url}"
        await self.redis.set(key, "true")

    async def acquire_download_lock(self, url: str, ttl: int = 60) -> bool:
        """
        Acquire a lock for downloading a given URL.

        Returns:
            bool: True if lock acquired, False if already locked.
        """
        lock_key = f"lock:{url}"
        return (await self.redis.set(lock_key, "in_progress", nx=True, ex=ttl)) is not None

    async def release_download_lock(self, url: str) -> None:
        """Release the lock for the given URL."""
        lock_key = f"lock:{url}"
        await self.redis.delete(lock_key)

    async def check_urls_batch(self, urls: List[str]) -> List[str]:
        """
        Given a batch of URLs, return only those that are not downloaded or not found.

        Args:
            urls (List[str]): A list of URLs to check.

        Returns:
            List[str]: URLs that are new and should be published for download.
        """
        if not urls:
            return []

        pipe = self.redis.pipeline()
        for url in urls:
            pipe.exists(f"downloaded:{url}")
        downloaded_results = await pipe.execute()

        pipe = self.redis.pipeline()
        for url in urls:
            pipe.exists(f"not_found:{url}")
        not_found_results = await pipe.execute()

        filtered = []
        for url, d_res, nf_res in zip(urls, downloaded_results, not_found_results):
            if d_res == 1 or nf_res == 1:
                continue
            filtered.append(url)

        return filtered

    async def close(self) -> None:
        """Close the Redis connection."""
        await self.redis.close()
        logger.info("Redis connection closed.")

redis_client = RedisClient()
