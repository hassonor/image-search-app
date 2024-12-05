import os
import asyncio
import time
import errno
from shutil import move
from itertools import islice
from asyncio import Semaphore, Lock, sleep

import aiohttp
from aiofiles import open as aio_open
from aiohttp_client_cache import CachedSession

from .config import (
    DATASET_FILE, OUTPUT_DIR, TEMP_DIR, CONCURRENT_REQUESTS, RETRIES, TIMEOUT,
    BATCH_SIZE, CHUNK_SIZE, CACHE_EXPIRATION
)

# Globals
semaphore = Semaphore(CONCURRENT_REQUESTS)
file_lock = Lock()
in_progress_lock = Lock()
in_progress_downloads = set()
request_count = 0


async def safe_move_file(temp_path: str, final_path: str, attempts: int = 3, wait: float = 0.2) -> None:
    """
    Safely move a file from temp_path to final_path, retrying if the file is locked.
    """
    for i in range(attempts):
        async with file_lock:
            try:
                if os.path.exists(temp_path):
                    if not os.path.exists(final_path):
                        move(temp_path, final_path)
                        return
                    else:
                        print(f"File already exists: {final_path}")
                        return
                else:
                    # Temp file is gone, possibly already moved.
                    return
            except PermissionError as e:
                if e.errno == errno.EACCES or e.winerror == 32:
                    print(f"File move locked, retrying {final_path} attempt {i + 1}/{attempts}")
                    await sleep(wait)
                else:
                    print(f"Error moving file {temp_path} to {final_path}: {e}")
                    return
            except Exception as e:
                print(f"Error moving file {temp_path} to {final_path}: {e}")
                return
    print(f"Failed to move file after {attempts} attempts: {temp_path} -> {final_path}")


async def download_image(client: aiohttp.ClientSession, url: str) -> None:
    """
    Download a single image from the given URL using the provided aiohttp client.
    Checks local existence, in-progress set, and performs safe moves after download.
    """
    global request_count
    file_name = os.path.basename(url.strip())
    final_path = os.path.join(OUTPUT_DIR, file_name)

    # Skip if file already exists
    if os.path.exists(final_path):
        print(f"File already exists locally, skipping: {final_path}")
        return

    temp_path = os.path.join(TEMP_DIR, file_name)

    # Prevent duplicate in-progress downloads
    async with in_progress_lock:
        if file_name in in_progress_downloads:
            return
        in_progress_downloads.add(file_name)

    try:
        async with semaphore:
            async with client.get(url.strip(), timeout=TIMEOUT) as response:
                if response.status == 200:
                    request_count += 1
                    async with aio_open(temp_path, 'wb') as f:
                        async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                            await f.write(chunk)

                    print(f"Downloaded: {url}")
                    await sleep(0.05)  # Ensure file handles closed on Windows
                    await safe_move_file(temp_path, final_path)
                else:
                    print(f"Failed to download {url}: HTTP {response.status}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
    finally:
        async with in_progress_lock:
            if file_name in in_progress_downloads:
                in_progress_downloads.remove(file_name)


async def download_with_retries(client: aiohttp.ClientSession, url: str) -> None:
    """
    Attempt to download the image multiple times in case of transient errors.
    """
    for attempt in range(RETRIES):
        try:
            await download_image(client, url)
            return
        except Exception as e:
            print(f"Retry {attempt + 1}/{RETRIES} for {url} failed: {e}")
            await sleep(2 ** attempt)
    print(f"Failed to download {url} after {RETRIES} retries.")


async def process_batch(client: aiohttp.ClientSession, urls: list) -> None:
    """
    Process a batch of URLs concurrently.
    """
    tasks = [download_with_retries(client, url) for url in urls]
    await asyncio.gather(*tasks)


def chunked_iterable(iterable, size):
    """
    Yield successive n-sized chunks from iterable.
    """
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk


async def main():
    """
    Main entry point for the downloader service.
    Reads URLs, deduplicates them, checks cache, and downloads images.
    """
    start_time = time.time()

    # Prepare directories
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Read and deduplicate URLs
    with open(DATASET_FILE, 'r') as f:
        all_urls = [url.strip() for url in f.readlines()]
    unique_urls = list(set(all_urls))
    print(f"Total URLs to process: {len(all_urls)}")
    print(f"Unique URLs after deduplication: {len(unique_urls)}")

    async with CachedSession(cache_name="http_cache", expire_after=CACHE_EXPIRATION) as cache_client:
        async with aiohttp.ClientSession() as stream_client:
            for batch in chunked_iterable(unique_urls, BATCH_SIZE):
                print(f"Processing batch of {len(batch)} URLs...")
                filtered_urls = []
                for url in batch:
                    # Check cache before adding the task
                    if not await cache_client.cache.has_url(url):
                        filtered_urls.append(url)
                    else:
                        print(f"URL cached or previously processed, skipping: {url}")

                await process_batch(stream_client, filtered_urls)

    elapsed_time = time.time() - start_time
    print(f"All downloads completed in {elapsed_time:.2f} seconds!")
    print(f"Total requests made: {request_count}")


if __name__ == "__main__":
    asyncio.run(main())
