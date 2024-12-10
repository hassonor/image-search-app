"""
redis_client.py

Manages Redis connections for caching URL states and distributed locks.
"""

import logging
from typing import List

import redis.asyncio as redis

from infrastructure.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for URL caching and lock handling."""

    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

    async def connect(self) -> None:
        """Check Redis connection by pinging."""
        try:
            await self.redis.ping()
            logger.info("Connected to Redis.")
        except Exception as e:
            logger.exception("Failed to connect to Redis: %s", e)
            raise

    async def is_url_downloaded(self, url: str) -> bool:
        key = f"downloaded:{url}"
        return (await self.redis.exists(key)) == 1

    async def cache_url_as_downloaded(self, url: str, file_path: str) -> None:
        key = f"downloaded:{url}"
        await self.redis.set(key, file_path)

    async def is_url_marked_as_not_found(self, url: str) -> bool:
        key = f"not_found:{url}"
        return (await self.redis.exists(key)) == 1

    async def cache_url_as_not_found(self, url: str) -> None:
        key = f"not_found:{url}"
        await self.redis.set(key, "true")

    async def acquire_download_lock(self, url: str, ttl: int = 60) -> bool:
        """
        Acquire a distributed lock to prevent concurrent downloads of the same URL.
        Returns True if lock acquired, False otherwise.
        """
        lock_key = f"lock:{url}"
        return (await self.redis.set(lock_key, "in_progress", nx=True, ex=ttl)) is not None

    async def release_download_lock(self, url: str) -> None:
        lock_key = f"lock:{url}"
        await self.redis.delete(lock_key)

    async def check_urls_batch(self, urls: List[str]) -> List[str]:
        """
        Filter a list of URLs to find those not already processed.

        Args:
            urls (List[str]): URLs to check.
        Returns:
            List[str]: Unprocessed URLs.
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
