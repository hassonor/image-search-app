import os
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
import asyncio
import aiofiles

async def retry_connection(connect_coro, max_retries=7, delay=10, name="service"):
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Connecting to {name} (attempt {attempt}/{max_retries})...")
            await connect_coro()
            logger.info(f"Connected to {name}.")
            return
        except Exception as e:
            logger.warning(f"Failed to connect to {name}: {e}")
            if attempt < max_retries:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
    logger.error(f"Could not connect to {name} after {max_retries} attempts.")
    raise ConnectionError(f"Failed to connect to {name}")

async def publish_embeddings(image_id: int, image_url: str, image_path: str):
    message = {
        "image_id": image_id,
        "image_url": image_url,
        "image_path": image_path
    }
    try:
        await rabbitmq_client.publish(settings.EMBEDDING_QUEUE, json.dumps(message))
        logger.info(f"Published embedding for image_id: {image_id}")
    except Exception as e:
        logger.exception(f"Failed to publish embedding for image_id {image_id}: {e}")

async def publish_urls(file_path: str):
    """
    Stream the file in chunks, check with Redis, and publish only URLs not processed.
    """
    if not file_path or not os.path.exists(file_path):
        logger.error(f"URL file not found: {file_path}")
        return

    chunk_size = settings.URL_CHUNK_SIZE
    urls_buffer = []

    async with aiofiles.open(file_path, 'r') as f:
        async for line in f:
            url = line.strip()
            if not url or url.startswith('#'):
                continue
            urls_buffer.append(url)

            if len(urls_buffer) >= chunk_size:
                await process_and_publish_chunk(urls_buffer)
                urls_buffer.clear()

    # Process remaining URLs
    if urls_buffer:
        await process_and_publish_chunk(urls_buffer)

async def process_and_publish_chunk(urls: list[str]):
    # Filter URLs by checking Redis in bulk
    urls_to_publish = await redis_client.check_urls_batch(urls)
    if not urls_to_publish:
        return

    logger.info(f"Publishing {len(urls_to_publish)} URLs to queue.")
    # Publish asynchronously to RabbitMQ
    for url in urls_to_publish:
        message = aio_pika.Message(body=json.dumps({"url": url}).encode())
        await rabbitmq_client.channel.default_exchange.publish(
            message, routing_key=settings.DOWNLOAD_QUEUE
        )
    logger.info("Chunk published.")

async def process_url(image_url: str, downloader_service: DownloaderService):
    result = await downloader_service.download_image(image_url)
    if result:
        image_id, image_path = result
        await publish_embeddings(image_id, image_url, image_path)

async def message_callback(url: str, downloader_service: DownloaderService):
    await process_url(url, downloader_service)

async def main():
    downloader_service = DownloaderService()
    try:
        await retry_connection(database.connect, name="PostgreSQL")
        await retry_connection(redis_client.connect, name="Redis")
        await retry_connection(rabbitmq_client.connect, name="RabbitMQ")

        start_metrics_server(port=settings.METRICS_PORT)

        async def callback(url: str):
            await message_callback(url, downloader_service)

        # Setup consumer
        await retry_connection(lambda: rabbitmq_client.consume(settings.DOWNLOAD_QUEUE, callback),
                               name="RabbitMQ Consumer")

        # Publish URLs from file in a streaming, chunked manner
        await publish_urls(settings.URLS_FILE_PATH)

        logger.info("Downloader service is running and ready to process messages.")
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info("Downloader service is shutting down.")
    except Exception as e:
        logger.exception(f"Service error: {e}")
    finally:
        await downloader_service.close()
        await rabbitmq_client.close()
        await redis_client.close()
        await database.close()

def shutdown():
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
