"""
infrastructure/rabbitmq_client.py

RabbitMQ client for consuming messages.
"""

import logging
import aio_pika
import asyncio
import json
from typing import Callable
from infrastructure.config import settings

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection: aio_pika.RobustConnection = None
        self.channel: aio_pika.RobustChannel = None

    async def connect(self):
        try:
            self.connection = await aio_pika.connect_robust(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                login=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASSWORD,
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=settings.NUM_CONSUMERS)
            logger.info("Connected to RabbitMQ.")
        except Exception as e:
            logger.exception("Failed to connect to RabbitMQ: %s", e)
            raise

    async def consume(self, queue_name: str, callback: Callable[[dict], asyncio.Future]):
        try:
            queue = await self.channel.declare_queue(queue_name, durable=True)
            await queue.consume(self._create_on_message(callback), no_ack=False)
            logger.info("Started consuming messages from queue: %s", queue_name)
        except Exception as e:
            logger.exception("Failed to start consuming from queue %s: %s", queue_name, e)
            raise

    def _create_on_message(self, callback: Callable[[dict], asyncio.Future]):
        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    body = message.body.decode()
                    data = json.loads(body)
                    image_id = data.get("image_id")
                    image_url = data.get("image_url")
                    if image_id and image_url:
                        logger.debug("Received image_id: %s, image_url: %s", image_id, image_url)
                        await callback(data)
                        logger.info("Processed image_id: %s", image_id)
                    else:
                        logger.warning("Incomplete message received: %s", body)
                except Exception as e:
                    logger.exception("Error processing message: %s", e)
        return on_message

    async def close(self):
        await self.connection.close()
        logger.info("RabbitMQ connection closed.")

rabbitmq_client = RabbitMQClient()
