"""
main.py

Main entry point for the Downloader Service.
Orchestrates startup connections, message consumption, URL publishing,
and runs a FastAPI server for documentation.
"""

import asyncio
import signal
from logging_config import logger
from metrics import start_metrics_server
from rabbitmq_client import rabbitmq_client
from download_service import DownloaderService
from redis_client import redis_client
from database import database
from config import settings
from server_runner import run_api_server
from startup import retry_connection
from messaging.callbacks import message_callback
from messaging.publishers import publish_urls


def shutdown():
    """
    Handle shutdown signals by canceling all running tasks.
    """
    logger.info("Shutdown signal received. Stopping service...")
    for task in asyncio.all_tasks():
        task.cancel()


async def main_async():
    """
    Asynchronous main entry point.
    Connects to services, starts metrics, sets up consumers, publishes initial URLs,
    and runs the API server.
    """
    downloader_service = DownloaderService(database=database, redis_client=redis_client)

    try:
        # Connect services
        await retry_connection(database.connect, name="PostgreSQL")
        await retry_connection(redis_client.connect, name="Redis")
        await retry_connection(rabbitmq_client.connect, name="RabbitMQ")

        # Start metrics server
        start_metrics_server(port=settings.METRICS_PORT)

        # Setup RabbitMQ consumer
        await retry_connection(
            lambda: rabbitmq_client.consume(
                settings.DOWNLOAD_QUEUE,
                lambda url: message_callback(url, downloader_service)
            ),
            name="RabbitMQ Consumer"
        )

        # Publish initial URLs from file
        await publish_urls(settings.URLS_FILE_PATH, settings.URL_CHUNK_SIZE)

        logger.info("Downloader service is running and ready to process messages.")

        # Run the API server in a background task
        api_task = asyncio.create_task(run_api_server())

        # Wait indefinitely until a shutdown signal is triggered
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
