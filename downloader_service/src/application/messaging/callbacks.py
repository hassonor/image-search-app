"""
callbacks.py

Message callbacks for handling incoming URLs from RabbitMQ.
"""

import logging
from typing import TYPE_CHECKING

from .publishers import publish_embeddings

if TYPE_CHECKING:
    from domain.download_service import DownloaderService

logger = logging.getLogger(__name__)


async def message_callback(url: str, downloader_service: "DownloaderService"):
    """
    Callback for handling incoming URLs from RabbitMQ.
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
