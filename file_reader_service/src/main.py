import asyncio
import signal

from application.publisher import publish_urls
from application.retry import retry_connection
from infrastructure.config import settings
from infrastructure.logging_config import logger
from infrastructure.metrics import start_metrics_server
from infrastructure.rabbitmq_client import rabbitmq_client
from infrastructure.redis_client import redis_client
from interface.api import run_api_server
from application.shutdown import shutdown
from domain.file_reader_service import FileReaderService

async def main_async():
    """
    Main entry point for the File Reader Service.
    """
    file_reader_service = FileReaderService(redis_client=redis_client)

    try:
        await retry_connection(redis_client.connect, name="Redis")
        await retry_connection(rabbitmq_client.connect, name="RabbitMQ")

        start_metrics_server(port=settings.METRICS_PORT)

        # Pre-warm Bloom filter if needed (optional; here just init is done in service init)
        logger.info("File Reader service starting...")

        await publish_urls(settings.URLS_FILE_PATH, settings.URL_CHUNK_SIZE, file_reader_service)

        logger.info("File Reader service has published initial URLs and is now running.")

        # Run API server for health checks
        api_task = asyncio.create_task(run_api_server(host="0.0.0.0", port=settings.API_PORT))

        # Wait indefinitely
        await asyncio.Event().wait()

    except asyncio.CancelledError:
        logger.info("File Reader service is shutting down due to signal.")
    except Exception as e:
        logger.exception("Service error: %s", e)
    finally:
        await rabbitmq_client.close()
        await redis_client.close()

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
        logger.info("File Reader service stopped.")
