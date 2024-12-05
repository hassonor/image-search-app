"""Utility functions for the image downloader service.

This module contains helper functions for safely moving files after downloading
and for chunking iterables into smaller parts.
"""

import os
import errno
from shutil import move
from itertools import islice
from asyncio import sleep

from logger import logger


async def safe_move_file(
    temp_path: str, final_path: str, attempts: int = 3, wait: float = 0.2
):
    """
    Safely move a file from temp_path to final_path, retrying on errors like file locks.

    Args:
        temp_path (str): The source file path.
        final_path (str): The destination file path.
        attempts (int): Number of retry attempts before giving up.
        wait (float): Wait time in seconds between retries.
    """
    final_dir = os.path.dirname(final_path)
    if not os.path.exists(final_dir):
        try:
            os.makedirs(final_dir)
            logger.info("Created directory: %s", final_dir)
        except OSError as e:
            logger.error("Failed to create directory %s: %s", final_dir, e)
            return

    for i in range(attempts):
        try:
            if os.path.exists(temp_path):
                if not os.path.exists(final_path):
                    move(temp_path, final_path)
                    logger.info("Moved %s to %s", temp_path, final_path)
                    return
                logger.warning("File exists: %s", final_path)
                return
            return
        except PermissionError as e:
            if e.errno == errno.EACCES or getattr(e, "winerror", None) == 32:
                logger.warning(
                    "File move locked, retrying %s attempt %d/%d",
                    final_path,
                    i + 1,
                    attempts,
                )
                await sleep(wait)
            else:
                logger.error("Error moving %s to %s: %s", temp_path, final_path, e)
                return
        except OSError as e:
            logger.error("OS error while moving file: %s", e)
            return
    logger.error(
        "Failed to move file after %d attempts: %s -> %s",
        attempts,
        temp_path,
        final_path,
    )


def chunked_iterable(iterable, size):
    """
    Yield successive n-sized chunks from the iterable.

    Args:
        iterable (iterable): The iterable to break into chunks.
        size (int): The number of items per chunk.

    Yields:
        list: A chunk of `size` items from `iterable`.
    """
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk
