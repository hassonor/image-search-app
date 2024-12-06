import redis.asyncio as redis
from config import settings
import logging

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for caching URLs."""

    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    async def connect(self):
        """Establish a connection to Redis."""
        try:
            await self.redis.ping()
            logger.info("Connected to Redis.")
        except Exception as e:
            logger.exception(f"Failed to connect to Redis: {e}")
            raise

    async def is_url_downloaded(self, url: str) -> bool:
        """Check if the URL has already been downloaded."""
        key = f"downloaded:{url}"
        return await self.redis.exists(key) == 1

    async def cache_url_as_downloaded(self, url: str, file_path: str):
        """Cache the downloaded URL with its file path."""
        key = f"downloaded:{url}"
        await self.redis.set(key, file_path)

    async def is_url_marked_as_not_found(self, url: str) -> bool:
        """Check if the URL is marked as not found."""
        key = f"not_found:{url}"
        return await self.redis.exists(key) == 1

    async def cache_url_as_not_found(self, url: str):
        """Cache the URL as not found."""
        key = f"not_found:{url}"
        await self.redis.set(key, "true")

    async def close(self):
        """Close the Redis connection."""
        await self.redis.close()
        logger.info("Redis connection closed.")


# Instantiate the RedisClient
redis_client = RedisClient()
