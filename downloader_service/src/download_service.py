"""
DownloaderService module.

Responsible for:
- Checking if a URL should be downloaded using Bloom filter, Redis, and locks.
- Downloading the image.
- Storing metadata in PostgreSQL.
- Reporting metrics.

Dependencies are injected via constructor for easier testing and flexibility.
"""

import logging
import os
import aiohttp
import asyncio
import hashlib
from typing import Optional, Tuple
from pybloom_live import BloomFilter
from config import settings
from redis_client import RedisClient
from database import Database
from metrics import images_downloaded, download_errors, download_latency

logger = logging.getLogger(__name__)

class DownloaderService:
    """
    Service for downloading images from URLs.

    It prevents duplicates using a Bloom filter, Redis caching, and distributed locks.
    Successfully downloaded images are stored locally and recorded in PostgreSQL.
    """

    def __init__(self, database: Database, redis_client: RedisClient):
        self.database = database
        self.redis_client = redis_client
        self.session = aiohttp.ClientSession(headers={"User-Agent": settings.USER_AGENT})
        self.bloom = BloomFilter(
            capacity=settings.BLOOM_EXPECTED_ITEMS,
            error_rate=settings.BLOOM_ERROR_RATE
        )
        self.lock = asyncio.Lock()

    async def download_image(self, url: str) -> Optional[Tuple[int, str]]:
        """
        Download the image from the given URL, store locally and record in DB.

        Steps:
            1. Acquire a Redis-based lock to prevent concurrent downloads.
            2. Check Bloom filter, Redis caches for duplicates.
            3. If new, download the image and store it.
            4. Record metadata in PostgreSQL.
            5. Update Redis and Bloom filter caches.

        Args:
            url (str): The image URL to download.

        Returns:
            Optional[Tuple[int, str]]: (image_id, local_path) if successful, None otherwise.
        """
        acquired = await self.redis_client.acquire_download_lock(url)
        if not acquired:
            logger.debug("URL currently locked: %s", url)
            return None

        try:
            async with self.lock:
                if url in self.bloom:
                    logger.debug("URL already in bloom filter: %s", url)
                    return None

            if await self.redis_client.is_url_downloaded(url):
                logger.debug("URL already downloaded (Redis): %s", url)
                return None

            if await self.redis_client.is_url_marked_as_not_found(url):
                logger.debug("URL marked not found: %s", url)
                return None

            logger.info("Starting download: %s", url)
            start_time = asyncio.get_event_loop().time()

            async with self.session.get(url, timeout=settings.DOWNLOAD_TIMEOUT) as response:
                if response.status == 404:
                    await self.redis_client.cache_url_as_not_found(url)
                    logger.warning("Image 404 Not Found: %s", url)
                    return None

                response.raise_for_status()
                content = await response.read()
                filename = self.generate_filename(url)
                local_path = os.path.join(settings.IMAGE_STORAGE_PATH, filename)

                os.makedirs(settings.IMAGE_STORAGE_PATH, exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(content)

                duration = asyncio.get_event_loop().time() - start_time
                download_latency.observe(duration)

                image_id = await self.database.store_image_record(url, local_path)
                if image_id:
                    await self.redis_client.cache_url_as_downloaded(url, local_path)
                    images_downloaded.inc()

                    async with self.lock:
                        self.bloom.add(url)

                    logger.info("Downloaded and stored: %s (ID: %d)", local_path, image_id)
                    return image_id, local_path
                else:
                    download_errors.inc()
                    logger.error("Failed to store metadata for URL: %s", url)
                    return None

        except aiohttp.ClientError as e:
            download_errors.inc()
            logger.error("ClientError downloading %s: %s", url, e)
            return None
        except Exception as e:
            download_errors.inc()
            logger.exception("Unexpected error downloading %s: %s", url, e)
            return None
        finally:
            await self.redis_client.release_download_lock(url)

    @staticmethod
    def generate_filename(url: str) -> str:
        """
        Generate a unique filename for the downloaded image based on the URL hash.

        Args:
            url (str): The image URL.

        Returns:
            str: A unique filename with extension derived from the URL.
        """
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        extension = os.path.splitext(url.split("?")[0])[1] or ".jpg"
        return f"{url_hash}{extension}"

    async def close(self) -> None:
        """Close the HTTP session."""
        await self.session.close()
        logger.info("DownloaderService session closed.")
