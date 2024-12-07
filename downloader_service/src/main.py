import asyncio
import signal
from logging_config import logger
from metrics import start_metrics_server
from rabbitmq_client import rabbitmq_client
from download_service import DownloaderService
from redis_client import redis_client
from database import database
from config import settings
import aio_pika
import json
import os

import asyncio
import time
from logging_config import logger


async def retry_connection(connect_coro, max_retries=5, delay=5, name="service"):
    """
    Attempts to run the `connect_coro` coroutine up to `max_retries` times,
    waiting `delay` seconds between retries.
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Trying to connect to {name} (attempt {attempt}/{max_retries})...")
            await connect_coro()
            logger.info(f"Successfully connected to {name}.")
            return
        except Exception as e:
            logger.warning(f"Failed to connect to {name} (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                logger.info(f"Waiting {delay} seconds before retrying...")
                await asyncio.sleep(delay)
    logger.error(f"Could not connect to {name} after {max_retries} attempts.")
    raise ConnectionError(f"Failed to connect to {name}")


async def publish_embeddings(image_id: int, image_url: str, image_path: str):
    """
    Publish a message to the image_embeddings queue with image_id and image_path.
    """
    message = {
        "image_id": image_id,
        "image_url": image_url,
        "image_path": image_path
    }
    try:
        await rabbitmq_client.publish(settings.EMBEDDING_QUEUE, json.dumps(message))
        logger.info(f"Published embedding message for image_id: {image_id}")
    except Exception as e:
        logger.exception(f"Failed to publish embedding message for image_id {image_id}: {e}")


async def publish_urls(file_path: str, rabbitmq_client, redis_client):
    """
    Read URLs from a file and publish them to RabbitMQ.
    Skip URLs already processed or marked as not found.
    """
    if not os.path.exists(file_path):
        logger.error(f"URL file not found: {file_path}")
        return

    with open(file_path, 'r') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]

    if not urls:
        logger.warning("No URLs found to publish.")
        return

    logger.info(f"Publishing {len(urls)} URLs from {file_path} to RabbitMQ.")

    for url in urls:
        # Check Redis to prevent duplicate publishing
        if await redis_client.is_url_downloaded(url) or await redis_client.is_url_marked_as_not_found(url):
            logger.debug(f"URL already processed or marked as not found: {url}, skipping.")
            continue

        try:
            message = aio_pika.Message(body=json.dumps({"url": url}).encode())
            await rabbitmq_client.channel.default_exchange.publish(
                message, routing_key=settings.DOWNLOAD_QUEUE
            )
            logger.info(f"Published URL: {url}")
        except Exception as e:
            logger.exception(f"Failed to publish URL {url}: {e}")

    logger.info("Completed publishing URLs.")


async def process_url(image_url: str, downloader_service: DownloaderService):
    """
    Callback function to process a single URL.
    """
    logger.debug(f"Processing URL: {image_url}")
    result = await downloader_service.download_image(image_url)
    if result:
        image_id, image_path = result
        await publish_embeddings(image_id, image_url, image_path)


async def message_callback(url: str, downloader_service: DownloaderService):
    """
    Wrapper callback to process the URL.
    """
    await process_url(url, downloader_service)


async def main():
    downloader_service = DownloaderService()
    try:
        # Initialize components with retries
        await retry_connection(database.connect, name="PostgreSQL")
        await retry_connection(redis_client.connect, name="Redis")
        await retry_connection(rabbitmq_client.connect, name="RabbitMQ")

        # Start metrics server
        start_metrics_server(port=8000)

        # Publish URLs
        urls_file = settings.URLS_FILE_PATH
        await publish_urls(urls_file, rabbitmq_client, redis_client)

        # Callback for message processing
        async def callback(url: str):
            await message_callback(url, downloader_service)

        # Start consuming messages with retry logic if needed
        # If you have a separate Elasticsearch connection step, also wrap it with retry_connection.
        await retry_connection(lambda: rabbitmq_client.consume(settings.DOWNLOAD_QUEUE, callback),
                               name="RabbitMQ Consumer")

        logger.info("Downloader service is running and ready to process messages.")

        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info("Downloader service is shutting down.")
    except Exception as e:
        logger.exception(f"Service encountered an error: {e}")
    finally:
        # Gracefully close connections
        await downloader_service.close()
        await rabbitmq_client.close()
        await redis_client.close()
        await database.close()


def shutdown():
    """
    Handle shutdown signals.
    """
    logger.info("Shutdown signal received. Stopping service...")
    for task in asyncio.all_tasks():
        task.cancel()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    try:
        loop.run_until_complete(main())
    except asyncio.CancelledError:
        pass
    finally:
        loop.close()
        logger.info("Downloader service stopped.")
