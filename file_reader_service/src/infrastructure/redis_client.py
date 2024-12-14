import logging
from typing import List
import redis.asyncio as redis
from infrastructure.config import settings

logger = logging.getLogger(__name__)

class RedisClient:
    def __init__(self):
        self.redis = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )

    async def connect(self) -> None:
        try:
            await self.redis.ping()
            logger.info("Connected to Redis.")
        except Exception as e:
            logger.exception("Failed to connect to Redis: %s", e)
            raise

    async def check_urls_batch(self, urls: List[str]) -> List[str]:
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
            # Only consider URL new if not marked as downloaded or not_found
            if d_res == 0 and nf_res == 0:
                filtered.append(url)

        return filtered

    async def close(self) -> None:
        await self.redis.close()
        logger.info("Redis connection closed.")

redis_client = RedisClient()
