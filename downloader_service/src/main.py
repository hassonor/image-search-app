import asyncio
import signal

from application.messaging.callbacks import message_callback
from application.retry import retry_connection
from application.server_runner import run_api_server
from application.shutdown import shutdown
from domain.download_service import DownloaderService
from infrastructure.config import settings
from infrastructure.database import database
from infrastructure.logging_config import logger
from infrastructure.metrics import start_metrics_server
from infrastructure.rabbitmq_client import rabbitmq_client
from infrastructure.redis_client import redis_client

async def main_async():
    downloader_service = DownloaderService(database=database, redis_client=redis_client)

    try:
        await retry_connection(database.connect, name="PostgreSQL")
        await retry_connection(redis_client.connect, name="Redis")
        await retry_connection(rabbitmq_client.connect, name="RabbitMQ")

        start_metrics_server(port=settings.METRICS_PORT)

        await retry_connection(
            lambda: rabbitmq_client.consume(
                settings.DOWNLOAD_QUEUE,
                lambda url: message_callback(url, downloader_service),
            ),
            name="RabbitMQ Consumer",
        )

        logger.info("Downloader service is running and ready to process messages.")

        api_task = asyncio.create_task(run_api_server())

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
