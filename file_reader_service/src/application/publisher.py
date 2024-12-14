import json
import logging
from typing import List
import os

import aiofiles
import aio_pika

from infrastructure.config import settings
from infrastructure.rabbitmq_client import rabbitmq_client
from domain.file_reader_service import FileReaderService

logger = logging.getLogger(__name__)

async def publish_urls(file_path: str, chunk_size: int, service: FileReaderService):
    """
    Read URLs from a file and publish them in chunks to the download queue.
    """
    if not file_path or not os.path.exists(file_path):
        logger.error("URL file not found: %s", file_path)
        return

    urls_buffer: List[str] = []
    async with aiofiles.open(file_path, "r") as f:
        async for line in f:
            url = line.strip()
            if not url or url.startswith("#"):
                continue
            urls_buffer.append(url)

            if len(urls_buffer) >= chunk_size:
                await process_and_publish_chunk(urls_buffer, service)
                urls_buffer.clear()

    if urls_buffer:
        await process_and_publish_chunk(urls_buffer, service)


async def process_and_publish_chunk(urls: List[str], service: FileReaderService):
    """
    Filter URLs using bloom filter & Redis, then publish new URLs to the download queue.
    """
    urls_to_publish = await service.filter_new_urls(urls)
    if not urls_to_publish:
        return

    logger.info("Publishing %d new URLs.", len(urls_to_publish))
    assert rabbitmq_client.channel is not None, "RabbitMQ channel not initialized."
    for url in urls_to_publish:
        message = aio_pika.Message(body=json.dumps({"url": url}).encode())
        await rabbitmq_client.channel.default_exchange.publish(
            message, routing_key=settings.DOWNLOAD_QUEUE
        )
    logger.info("Chunk published.")
