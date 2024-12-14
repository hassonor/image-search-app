import json
import logging

from infrastructure.config import settings
from infrastructure.rabbitmq_client import rabbitmq_client

logger = logging.getLogger(__name__)


async def publish_embeddings(image_id: int, image_url: str, image_path: str):
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
