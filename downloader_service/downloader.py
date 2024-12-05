"""This module provides the ImageDownloader class for concurrent image downloading,
utilizing async/await, concurrency controls, and safe file operations.
"""

import os
from asyncio import Semaphore, Lock
import aiohttp
from aiofiles import open as aio_open
from config import CHUNK_SIZE, TIMEOUT
from utils import safe_move_file
from logger import logger


class ImageDownloader:
    """
    Handles downloading and saving images from URLs concurrently.
    It uses a semaphore to limit concurrent downloads, locks to ensure thread-safe
    file operations, and maintains a record of downloads in progress.
    """

    def __init__(self, config: dict):
        """
        Initialize the ImageDownloader with a configuration dictionary.

        Args:
            config (dict): A dictionary with:
                - 'semaphore' (Semaphore): concurrency semaphore.
                - 'file_lock' (Lock): lock for file operations.
                - 'in_progress_lock' (Lock): lock for tracking in-progress downloads.
                - 'output_dir' (str): directory to store final files.
                - 'temp_dir' (str): directory to store temporary files.
        """
        self.semaphore: Semaphore = config["semaphore"]
        self.file_lock: Lock = config["file_lock"]
        self.in_progress_lock: Lock = config["in_progress_lock"]
        self.output_dir: str = config["output_dir"]
        self.temp_dir: str = config["temp_dir"]
        self.request_count: int = 0
        self.in_progress_downloads = set()

    async def download_image(self, client: aiohttp.ClientSession, url: str) -> None:
        """
        Download an image from the given URL and save it to the output directory.
        If the file already exists, it skips the download.
        Uses safe_move_file to ensure no conflicts during file moves.

        Args:
            client (aiohttp.ClientSession): The HTTP client session for requests.
            url (str): The image URL.
        """
        file_name = url.strip().split("/")[-1]
        final_path = os.path.join(self.output_dir, file_name)

        if os.path.exists(final_path):
            logger.info("File exists: %s", final_path)
            return

        temp_path = os.path.join(self.temp_dir, file_name)

        async with self.in_progress_lock:
            if file_name in self.in_progress_downloads:
                return
            self.in_progress_downloads.add(file_name)

        try:
            async with self.semaphore:
                async with client.get(url, timeout=TIMEOUT) as response:
                    if response.status == 200:
                        self.request_count += 1
                        async with aio_open(temp_path, "wb") as f:
                            async for chunk in response.content.iter_chunked(
                                CHUNK_SIZE
                            ):
                                await f.write(chunk)
                        await safe_move_file(temp_path, final_path)
                        logger.info("Downloaded: %s", url)
                    else:
                        logger.error("Failed %s: HTTP %d", url, response.status)
        except aiohttp.ClientError as e:
            logger.error("Network error downloading %s: %s", url, e)
        except OSError as e:
            logger.error("OS error during download of %s: %s", url, e)
        except RuntimeError as e:
            logger.error("Runtime error downloading %s: %s", url, e)
        finally:
            async with self.in_progress_lock:
                self.in_progress_downloads.discard(file_name)

    def get_request_count(self) -> int:
        """
        Return the number of successful download requests made.

        Returns:
            int: The count of successfully downloaded images.
        """
        return self.request_count
