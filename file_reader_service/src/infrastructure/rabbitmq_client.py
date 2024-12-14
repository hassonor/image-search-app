import logging
import aio_pika
from infrastructure.config import settings

logger = logging.getLogger(__name__)

class RabbitMQClient:
    def __init__(self):
        self.connection = None
        self.channel = None

    async def connect(self) -> None:
        try:
            self.connection = await aio_pika.connect_robust(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                login=settings.RABBITMQ_USER,
                password=settings.RABBITMQ_PASSWORD,
            )
            self.channel = await self.connection.channel()
            logger.info("Connected to RabbitMQ.")
        except Exception as e:
            logger.exception("Failed to connect to RabbitMQ: %s", e)
            raise

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()
        logger.info("RabbitMQ connection closed.")

rabbitmq_client = RabbitMQClient()
