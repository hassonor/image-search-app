"""
main.py

Main entry point for the Downloader Service.

Orchestrates:
- Connecting to PostgreSQL, Redis, RabbitMQ with retries.
- Starting the Prometheus metrics server.
- Consuming messages for image downloads.
- Publishing initial URLs from a file.
- Running a FastAPI server for docs.
- Handling graceful shutdown signals.
"""

import asyncio
import signal
from infrastructure.logging_config import logger
from infrastructure.metrics import start_metrics_server
from infrastructure.rabbitmq_client import rabbitmq_client
from domain.download_service import DownloaderService
from infrastructure.redis_client import redis_client
from infrastructure.database import database
from infrastructure.config import settings
from application.server_runner import run_api_server
from application.retry import retry_connection
from application.shutdown import shutdown
from application.messaging.callbacks import message_callback
from application.messaging.publishers import publish_urls

async def main_async():
    """
    Asynchronous main function to run the downloader service.
    """
    downloader_service = DownloaderService(database=database, redis_client=redis_client)

    try:
        # Connect services with retries
        await retry_connection(database.connect, name="PostgreSQL")
        await retry_connection(redis_client.connect, name="Redis")
        await retry_connection(rabbitmq_client.connect, name="RabbitMQ")

        # Start metrics server
        start_metrics_server(port=settings.METRICS_PORT)

        # Setup RabbitMQ consumer for downloading images
        await retry_connection(
            lambda: rabbitmq_client.consume(
                settings.DOWNLOAD_QUEUE,
                lambda url: message_callback(url, downloader_service)
            ),
            name="RabbitMQ Consumer"
        )

        # Publish initial URLs from input file
        await publish_urls(settings.URLS_FILE_PATH, settings.URL_CHUNK_SIZE)

        logger.info("Downloader service is running and ready to process messages.")

        # Run the API server in background
        api_task = asyncio.create_task(run_api_server())

        # Wait indefinitely until a shutdown signal
        await asyncio.Event().wait()

    except asyncio.CancelledError:
        logger.info("Downloader service is shutting down due to signal.")
    except Exception as e:
        logger.exception("Service error: %s", e)
    finally:
        await downloader_service.close()
        await rabbitmq_client.close()
        await redis_client.close()
        await database.close()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    try:
        loop.run_until_complete(main_async())
    except asyncio.CancelledError:
        pass
    finally:
        loop.close()
        logger.info("Downloader service stopped.")
