import asyncio
import signal

from embedding_service import EmbeddingService
from logging_config import logger
from metrics import start_metrics_server, embeddings_generated, embedding_errors, embedding_latency
from rabbitmq_client import rabbitmq_client
from elasticsearch_client import elasticsearch_client

from config import settings

logger = logger  # From logging_config.py


async def process_message(data: dict, embedding_service: EmbeddingService):
    """
    Process a single message: generate embedding and index it.
    """
    image_id = data.get("image_id")
    image_url = data.get("image_url")
    image_path = data.get("image_path")

    if not image_id or not image_url or not image_path:
        logger.warning("Invalid message data: %s", data)
        return

    embedding = embedding_service.generate_embedding_from_image(image_path)
    if embedding:
        try:
            start_time = asyncio.get_event_loop().time()
            await elasticsearch_client.index_embedding(image_id, image_url,image_path, embedding)
            duration = asyncio.get_event_loop().time() - start_time
            embedding_latency.observe(duration)
            embeddings_generated.inc()
            logger.info(f"Processed and indexed embedding for image_id: {image_id}")
        except Exception as e:
            embedding_errors.inc()
            logger.error(f"Failed to index embedding for image_id: {image_id}: {e}")
    else:
        embedding_errors.inc()
        logger.error(f"Failed to generate embedding for image_id: {image_id}")


async def main():
    """
    Main entry point for the Embedding Generator Service.
    """
    embedding_service = EmbeddingService()
    try:
        # Initialize components
        await elasticsearch_client.create_index()
        await rabbitmq_client.connect()
        start_metrics_server(port=settings.METRICS_PORT)

        # Start consuming messages
        await rabbitmq_client.consume(settings.EMBEDDING_QUEUE, lambda data: process_message(data, embedding_service))

        logger.info("Embedding Generator Service is running and ready to process messages.")

        # Keep the service running
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        logger.info("Embedding Generator Service is shutting down.")
    except Exception as e:
        logger.exception(f"Service encountered an error: {e}")
    finally:
        # Gracefully close connections
        if embedding_service.model:
            embedding_service.model.cpu()
        await elasticsearch_client.close()
        await rabbitmq_client.close()


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
        logger.info("Embedding Generator Service stopped.")
