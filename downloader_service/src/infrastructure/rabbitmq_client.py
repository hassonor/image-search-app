"""
rabbitmq_client.py

RabbitMQ client for connecting, consuming, and publishing messages.
"""

import logging
import aio_pika
import asyncio
import json
from typing import Callable, Awaitable
from infrastructure.config import settings

logger = logging.getLogger(__name__)

class RabbitMQClient:
    """RabbitMQ client for message consumption and publication."""
    def __init__(self):
        self.connection: aio_pika.RobustConnection = None
        self.channel: aio_pika.RobustChannel = None

    async def connect(self) -> None:
        """Connect to RabbitMQ and initialize a channel."""
        try:
            self.connection = await aio_pika.connect_robust(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                login=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASSWORD
            )
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=settings.NUM_CONSUMERS)
            logger.info("Connected to RabbitMQ.")
        except Exception as e:
            logger.exception("Failed to connect to RabbitMQ: %s", e)
            raise

    async def consume(self, queue_name: str, callback: Callable[[str], Awaitable[None]]) -> None:
        """
        Start consuming messages from the given queue using the provided callback.

        Args:
            queue_name (str): Name of the RabbitMQ queue.
            callback (Callable[[str], Awaitable[None]]):
                Async function to process the received message.
        """
        try:
            queue = await self.channel.declare_queue(queue_name, durable=True)
            await queue.consume(self._create_on_message(callback), no_ack=False)
            logger.info("Started consuming messages from queue: %s", queue_name)
        except Exception as e:
            logger.exception("Error setting up consumer: %s", e)
            raise

    def _create_on_message(self, callback: Callable[[str], Awaitable[None]]):
        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    body = message.body.decode()
                    data = json.loads(body)
                    url = data.get("url")
                    if url:
                        logger.debug("Received URL: %s", url)
                        await callback(url)
                        logger.debug("Processed URL: %s", url)
                    else:
                        logger.warning("Received message without 'url': %s", body)
                except Exception as e:
                    logger.exception("Error processing message: %s", e)
        return on_message

    async def publish(self, queue_name: str, message: str) -> None:
        """
        Publish a message to a specified queue.

        Args:
            queue_name (str): Target RabbitMQ queue.
            message (str): JSON string of the message to publish.
        """
        try:
            queue = await self.channel.declare_queue(queue_name, durable=True)
            await self.channel.default_exchange.publish(
                aio_pika.Message(body=message.encode()),
                routing_key=queue.name
            )
            logger.debug("Published message to %s: %s", queue_name, message)
        except Exception as e:
            logger.exception("Failed to publish message to %s: %s", queue_name, e)
            raise

    async def close(self) -> None:
        """Close the RabbitMQ connection."""
        if self.connection:
            await self.connection.close()
        logger.info("RabbitMQ connection closed.")

rabbitmq_client = RabbitMQClient()
