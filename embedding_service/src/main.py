"""
main.py

Main entry point for the Embedding Generator Service.
Orchestrates:
- Connection retries to Elasticsearch and RabbitMQ.
- Starting metrics server.
- Consuming messages to generate and index embeddings.
- Graceful shutdown.
"""

import asyncio
import signal


from infrastructure.logging_config import logger
from infrastructure.metrics import start_metrics_server
from infrastructure.rabbitmq_client import rabbitmq_client
from infrastructure.elasticsearch_client import elasticsearch_client
from infrastructure.config import settings
from domain.embedding_service import EmbeddingService
from application.retry import retry_connection
from application.message_processor import process_message
from application.shutdown import shutdown
from application.server_runner import run_api_server

logger = logger

async def main():
    embedding_service = EmbeddingService()
    try:
        await elasticsearch_client.create_index()

        # Use retry logic for RabbitMQ connection
        await retry_connection(rabbitmq_client.connect, name="RabbitMQ")

        # Use retry logic for starting the consumer
        await retry_connection(
            lambda: rabbitmq_client.consume(settings.EMBEDDING_QUEUE, lambda data: process_message(data, embedding_service)),
            name="RabbitMQ Consumer"
        )

        # Start metrics server after consumer is ready
        start_metrics_server(port=settings.METRICS_PORT)

        # Run the API server in background
        api_task = asyncio.create_task(run_api_server())

        logger.info("Embedding Generator Service is running and ready to process messages.")
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info("Embedding Generator Service is shutting down.")
    except Exception as e:
        logger.exception("Service encountered an error: %s", e)
    finally:
        if embedding_service.model:
            embedding_service.model.cpu()
        await elasticsearch_client.close()
        await rabbitmq_client.close()

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
        logger.info("Embedding Generator Service stopped.")
