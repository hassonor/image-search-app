import redis.asyncio as redis
from config import settings
import logging

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True
        )

    async def connect(self):
        try:
            await self.redis.ping()
            logger.info("Connected to Redis.")
        except Exception as e:
            logger.exception("Failed to connect to Redis: %s", e)
            raise

    async def is_url_downloaded(self, url: str) -> bool:
        key = f"downloaded:{url}"
        return (await self.redis.exists(key)) == 1

    async def cache_url_as_downloaded(self, url: str, file_path: str):
        key = f"downloaded:{url}"
        await self.redis.set(key, file_path)

    async def is_url_marked_as_not_found(self, url: str) -> bool:
        key = f"not_found:{url}"
        return (await self.redis.exists(key)) == 1

    async def cache_url_as_not_found(self, url: str):
        key = f"not_found:{url}"
        await self.redis.set(key, "true")

    async def acquire_download_lock(self, url: str, ttl=60) -> bool:
        lock_key = f"lock:{url}"
        return (await self.redis.set(lock_key, "in_progress", nx=True, ex=ttl)) is not None

    async def release_download_lock(self, url: str):
        lock_key = f"lock:{url}"
        await self.redis.delete(lock_key)

    async def check_urls_batch(self, urls: list[str]) -> list[str]:
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

    async def close(self):
        await self.redis.close()
        logger.info("Redis connection closed.")

redis_client = RedisClient()
