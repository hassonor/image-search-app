import logging
import aio_pika
import asyncio
import json
from typing import Callable
from config import settings

logger = logging.getLogger(__name__)

class RabbitMQClient:
    """RabbitMQ client for consuming and publishing messages."""

    def __init__(self):
        self.connection: aio_pika.RobustConnection = None
        self.channel: aio_pika.RobustChannel = None

    async def connect(self):
        """Establish a connection and channel to RabbitMQ."""
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

    async def consume(self, queue_name: str, callback: Callable[[str], asyncio.Future]):
        """
        Asynchronously consume messages from the given queue and process them using the callback.
        """
        try:
            queue = await self.channel.declare_queue(queue_name, durable=True)
            await queue.consume(self._create_on_message(callback), no_ack=False)
            logger.info("Started consuming messages from queue: %s", queue_name)
        except Exception as e:
            logger.exception("Error setting up consumer: %s", e)
            raise

    def _create_on_message(self, callback: Callable[[str], asyncio.Future]):
        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    body = message.body.decode()
                    data = json.loads(body)
                    url = data.get("url")
                    if url:
                        logger.debug("Received URL: %s", url)
                        await callback(url)
                        logger.info("Processed URL: %s", url)
                    else:
                        logger.warning("Received message without URL: %s", body)
                except Exception as e:
                    logger.exception("Error processing message: %s", e)
                    # Optionally, you can requeue the message or send to a dead-letter queue
        return on_message

    async def publish(self, queue_name: str, message: str):
        """Asynchronously publish a message to the specified RabbitMQ queue."""
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

    async def close(self):
        """Close the RabbitMQ connection."""
        await self.connection.close()
        logger.info("RabbitMQ connection closed.")


rabbitmq_client = RabbitMQClient()
