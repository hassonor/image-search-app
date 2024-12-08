"""
application/message_processor.py

Processes incoming messages to generate embeddings and index them.
"""

import asyncio
import logging
from infrastructure.metrics import embeddings_generated, embedding_errors, embedding_latency
from infrastructure.elasticsearch_client import elasticsearch_client
from domain.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

async def process_message(data: dict, embedding_service: EmbeddingService):
    image_id = data.get("image_id")
    image_url = data.get("image_url")
    image_path = data.get("image_path")

    if not image_id or not image_url or not image_path:
        logger.warning("Invalid message data: %s", data)
        return

    embedding = embedding_service.generate_embedding_from_image(image_path)
    if embedding:
        try:
            start_time = asyncio.get_running_loop().time()
            await elasticsearch_client.index_embedding(image_id, image_url, image_path, embedding)
            duration = asyncio.get_running_loop().time() - start_time
            embedding_latency.observe(duration)
            embeddings_generated.inc()
            logger.info("Processed and indexed embedding for image_id: %s", image_id)
        except Exception as e:
            embedding_errors.inc()
            logger.error("Failed to index embedding for image_id %s: %s", image_id, e)
    else:
        embedding_errors.inc()
        logger.error("Failed to generate embedding for image_id: %s", image_id)
