"""Main entry point for the downloader service.

This module orchestrates:
- Reading and deduplicating URLs from a dataset.
- Initializing and using the ImageDownloader to download images.
- Utilizing caching to avoid re-downloading the same URLs multiple times.
"""

import asyncio
from asyncio import Semaphore, Lock

from aiohttp import ClientSession
from aiohttp_client_cache import CachedSession

# Local imports (ensure __init__.py is in downloader_service directory)
from downloader import ImageDownloader
from config import DATASET_FILE, OUTPUT_DIR, TEMP_DIR, CONCURRENT_REQUESTS, BATCH_SIZE
from utils import chunked_iterable
from logger import logger


async def main():
    """
    Main asynchronous function that:
    - Reads URLs from DATASET_FILE
    - Deduplicates URLs
    - Downloads images in batches using ImageDownloader
    - Utilizes caching via CachedSession
    """
    downloader = ImageDownloader(
        {
            "semaphore": Semaphore(CONCURRENT_REQUESTS),
            "file_lock": Lock(),
            "in_progress_lock": Lock(),
            "output_dir": OUTPUT_DIR,
            "temp_dir": TEMP_DIR,
        }
    )

    # Specify encoding to address W1514
    with open(DATASET_FILE, "r", encoding="utf-8") as f:
        all_urls = [url.strip() for url in f.readlines()]
    unique_urls = list(set(all_urls))

    logger.info("Total URLs: %d | Unique URLs: %d", len(all_urls), len(unique_urls))

    async with CachedSession() as cache_client, ClientSession() as client:
        for batch in chunked_iterable(unique_urls, BATCH_SIZE):
            logger.info("Processing batch of %d URLs...", len(batch))
            filtered_urls = [
                url for url in batch if not await cache_client.cache.has_url(url)
            ]
            await asyncio.gather(
                *(downloader.download_image(client, url) for url in filtered_urls)
            )


if __name__ == "__main__":
    asyncio.run(main())
