"""
domain/download_service.py

Defines the DownloaderService class responsible for downloading images,
avoiding duplicates, and recording metadata in the database.
"""

import asyncio
import hashlib
import logging
import os
from typing import Optional, Tuple

import aiohttp
from pybloom_live import BloomFilter

from infrastructure.config import settings
from infrastructure.database import Database
from infrastructure.metrics import download_errors, download_latency, images_downloaded
from infrastructure.redis_client import RedisClient

logger = logging.getLogger(__name__)


class DownloaderService:
    """
    Service for handling image downloads:
    - Checks Bloom filter, Redis caches, and distributed locks to prevent duplicates.
    - Downloads images and stores them locally and in PostgreSQL.
    - Tracks download metrics.
    """

    def __init__(self, database: Database, redis_client: RedisClient):
        self.database = database
        self.redis_client = redis_client
        self.session = aiohttp.ClientSession(headers={"User-Agent": settings.USER_AGENT})
        self.bloom = BloomFilter(
            capacity=settings.BLOOM_EXPECTED_ITEMS, error_rate=settings.BLOOM_ERROR_RATE
        )
        self.lock = asyncio.Lock()

    async def download_image(self, url: str) -> Optional[Tuple[int, str]]:
        """
        Download the image from the given URL if not already processed.

        Steps:
            1. Acquire distributed lock.
            2. Check Bloom filter and Redis caches.
            3. Validate URL before download.
            4. If new, download and store image, record in DB.
            5. Mark as downloaded in Redis and Bloom filter, update metrics.

        Args:
            url (str): Image URL to download.

        Returns:
            Optional[Tuple[int, str]]: (image_id, local_path) if successful, else None.
        """
        acquired = await self.redis_client.acquire_download_lock(url)
        if not acquired:
            logger.debug("URL locked: %s", url)
            return None

        try:
            # Validate URL format early, to avoid unnecessary network calls.
            if not self.is_valid_url(url):
                download_errors.inc()
                logger.error("Invalid URL format: %s", url)
                return None

            async with self.lock:
                if url in self.bloom:
                    logger.debug("URL in bloom filter: %s", url)
                    return None

            if await self.redis_client.is_url_downloaded(url):
                logger.debug("URL already downloaded (Redis): %s", url)
                return None

            if await self.redis_client.is_url_marked_as_not_found(url):
                logger.debug("URL marked not found: %s", url)
                return None

            logger.info("Downloading: %s", url)
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

        except aiohttp.ClientConnectorError as e:
            # Networking issues, DNS errors, refused connections
            download_errors.inc()
            logger.error("ConnectionError downloading %s: %s", url, e)
            return None
        except aiohttp.ClientResponseError as e:
            # Non-200 status codes (other than 404 handled above), request issues
            download_errors.inc()
            logger.error("HTTP error downloading %s: %s (status: %d)", url, e, e.status)
            return None
        except aiohttp.ClientError as e:
            # Generic client error (e.g., invalid URL scheme, SSL error)
            download_errors.inc()
            logger.error("ClientError downloading %s: %s", url, e)
            return None
        except Exception as e:
            # Unexpected errors
            download_errors.inc()
            logger.exception("Unexpected error downloading %s: %s", url, e)
            return None
        finally:
            await self.redis_client.release_download_lock(url)

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate the URL format before attempting to download.
        This helps fail fast on clearly malformed URLs.
        """
        from urllib.parse import urlparse

        parsed = urlparse(url)
        return all([parsed.scheme in ("http", "https"), parsed.netloc])

    @staticmethod
    def generate_filename(url: str) -> str:
        """
        Generate a unique filename for the downloaded image based on the URL hash.

        Args:
            url (str): The image URL.

        Returns:
            str: A unique filename with an extension derived from the URL.
        """
        import os

        url_hash = hashlib.sha256(url.encode()).hexdigest()
        extension = os.path.splitext(url.split("?")[0])[1] or ".jpg"
        return f"{url_hash}{extension}"
