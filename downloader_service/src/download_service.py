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
    """Service to handle downloading images from URLs."""

    def __init__(self):
        self.session = aiohttp.ClientSession(headers={"User-Agent": settings.USER_AGENT})
        self.bloom = BloomFilter(capacity=settings.BLOOM_EXPECTED_ITEMS, error_rate=settings.BLOOM_ERROR_RATE)
        self.lock = asyncio.Lock()

    async def download_image(self, url: str) -> Optional[Tuple[int, str]]:
        """
        Asynchronously download the image from the given URL and return the local file path.
        Checks Redis and Bloom filter for deduplication.
        """
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
                    image_path = local_path
                    return image_id, image_path
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

    @staticmethod
    def generate_filename(url: str, response: aiohttp.ClientResponse) -> str:
        """
        Generate a unique filename for the downloaded image.
        """
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        extension = os.path.splitext(url.split("?")[0])[1] or ".jpg"
        return f"{url_hash}{extension}"

    async def close(self):
        """Close the HTTP session."""
        await self.session.close()
        logger.info("HTTP session closed.")
