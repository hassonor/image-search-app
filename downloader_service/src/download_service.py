"""
Downloader Service module.

This service handles the download of images from provided URLs.
It uses an asynchronous HTTP client (aiohttp) with a specified timeout,
checks a Bloom filter and Redis caches to prevent duplicates, and
stores downloaded images in a local directory. It also logs download metrics.
"""

import logging
import os
import aiohttp
import asyncio
import hashlib
from typing import Optional, Tuple
from pybloom_live import BloomFilter
from config import settings
from redis_client import redis_client
from database import database
from metrics import images_downloaded, download_errors, download_latency

logger = logging.getLogger(__name__)

class DownloaderService:
    """
    Service to handle downloading images from URLs.

    This service ensures that each URL is downloaded once by using a Bloom filter,
    Redis caching, and distributed locks. Downloaded images are persisted locally,
    and records are stored in PostgreSQL.
    """

    def __init__(self):
        """
        Initialize the DownloaderService with an HTTP session and Bloom filter.
        """
        self.session = aiohttp.ClientSession(headers={"User-Agent": settings.USER_AGENT})
        self.bloom = BloomFilter(capacity=settings.BLOOM_EXPECTED_ITEMS, error_rate=settings.BLOOM_ERROR_RATE)
        self.lock = asyncio.Lock()

    async def download_image(self, url: str) -> Optional[Tuple[int, str]]:
        """
        Asynchronously download the image from the given URL and return the (image_id, file_path).

        This method checks Redis and the Bloom filter to skip duplicates,
        and uses a distributed lock in Redis to prevent concurrent downloads of the same URL.
        """
        # Acquire a distributed lock to prevent concurrent downloads of the same URL
        acquired = await redis_client.acquire_download_lock(url)
        if not acquired:
            logger.debug("Another consumer is already processing this URL, skipping: %s", url)
            return None

        try:
            async with self.lock:
                if url in self.bloom:
                    logger.debug("URL already processed (Bloom filter), skipping: %s", url)
                    return None

            if await redis_client.is_url_downloaded(url):
                logger.debug("URL already downloaded, skipping: %s", url)
                return None

            if await redis_client.is_url_marked_as_not_found(url):
                logger.debug("URL marked as not found, skipping: %s", url)
                return None

            logger.info("Downloading image from URL: %s", url)
            start_time = asyncio.get_event_loop().time()

            try:
                async with self.session.get(url, timeout=settings.DOWNLOAD_TIMEOUT) as response:
                    if response.status == 404:
                        await redis_client.cache_url_as_not_found(url)
                        logger.warning("Image not found (404): %s", url)
                        return None

                    response.raise_for_status()

                    content = await response.read()
                    filename = self.generate_filename(url, response)
                    local_path = os.path.join(settings.IMAGE_STORAGE_PATH, filename)

                    os.makedirs(settings.IMAGE_STORAGE_PATH, exist_ok=True)
                    with open(local_path, "wb") as f:
                        f.write(content)

                    duration = asyncio.get_event_loop().time() - start_time
                    download_latency.observe(duration)

                    image_id = await database.store_image_record(url, local_path)
                    if image_id:
                        await redis_client.cache_url_as_downloaded(url, local_path)
                        images_downloaded.inc()

                        async with self.lock:
                            self.bloom.add(url)

                        logger.info("Image downloaded and stored at: %s with ID: %s", local_path, image_id)
                        return image_id, local_path
                    else:
                        download_errors.inc()
                        logger.error("Failed to retrieve image ID for URL: %s", url)
                        return None

            except aiohttp.ClientError as e:
                download_errors.inc()
                logger.error("Failed to download image %s: %s", url, e)
                return None
            except Exception as e:
                download_errors.inc()
                logger.exception("Unexpected error downloading image %s: %s", url, e)
                return None

        finally:
            # Release the lock regardless of success or failure
            await redis_client.release_download_lock(url)

    @staticmethod
    def generate_filename(url: str, response: aiohttp.ClientResponse) -> str:
        """
        Generate a unique filename for the downloaded image based on the URL's hash.
        """
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        extension = os.path.splitext(url.split("?")[0])[1] or ".jpg"
        return f"{url_hash}{extension}"

    async def close(self):
        """Close the HTTP session."""
        await self.session.close()
        logger.info("HTTP session closed.")
