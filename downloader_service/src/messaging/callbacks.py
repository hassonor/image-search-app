"""
messaging/callbacks.py

Contains callbacks for handling incoming messages from RabbitMQ queues.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from download_service import DownloaderService

from .publishers import publish_embeddings

logger = logging.getLogger(__name__)


async def message_callback(url: str, downloader_service: "DownloaderService"):
    """
    Callback executed when a message (URL) is received from the download queue.
    """
    await process_url(url, downloader_service)


async def process_url(url: str, downloader_service: "DownloaderService"):
    """
    Process a single URL by downloading the image and publishing an embedding task.
    """
    result = await downloader_service.download_image(url)
    if result:
        image_id, image_path = result
        await publish_embeddings(image_id, url, image_path)
