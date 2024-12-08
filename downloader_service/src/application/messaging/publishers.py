"""
publishers.py

Functions to publish messages to RabbitMQ queues and handle initial URL publishing.
"""

import json
import logging
from typing import List
import aio_pika
from infrastructure.config import settings
from infrastructure.redis_client import redis_client
from infrastructure.rabbitmq_client import rabbitmq_client

logger = logging.getLogger(__name__)

async def publish_embeddings(image_id: int, image_url: str, image_path: str):
    """
    Publish a message to the embedding queue to process embeddings for the downloaded image.
    """
    message = {
        "image_id": image_id,
        "image_url": image_url,
        "image_path": image_path,
    }
    try:
        await rabbitmq_client.publish(settings.EMBEDDING_QUEUE, json.dumps(message))
        logger.info("Published embedding for image_id: %d", image_id)
    except Exception as e:
        logger.exception("Failed to publish embedding for image_id %d: %s", image_id, e)

async def publish_urls(file_path: str, chunk_size: int):
    """
    Read URLs from a file and publish them in chunks to the download queue.

    Args:
        file_path (str): Path to the file containing URLs.
        chunk_size (int): Number of URLs to process at a time.
    """
    import os
    import aiofiles

    if not file_path or not os.path.exists(file_path):
        logger.error("URL file not found: %s", file_path)
        return

    urls_buffer: List[str] = []

    async with aiofiles.open(file_path, 'r') as f:
        async for line in f:
            url = line.strip()
            if not url or url.startswith('#'):
                continue
            urls_buffer.append(url)

            if len(urls_buffer) >= chunk_size:
                await process_and_publish_chunk(urls_buffer)
                urls_buffer.clear()

    if urls_buffer:
        await process_and_publish_chunk(urls_buffer)

async def process_and_publish_chunk(urls: List[str]):
    """
    Filter and publish new URLs to the download queue.

    Args:
        urls (List[str]): URLs to process.
    """
    urls_to_publish = await redis_client.check_urls_batch(urls)
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
