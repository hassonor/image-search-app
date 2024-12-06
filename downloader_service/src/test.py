import asyncio
import json
import aio_pika
from config import settings

async def publish_message(url: str):
    connection = await aio_pika.connect_robust(
        host=settings.RABBITMQ_HOST,
        port=settings.RABBITMQ_PORT,
        login=settings.RABBITMQ_USER,
        password=settings.RABBITMQ_PASSWORD
    )
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(settings.DOWNLOAD_QUEUE, durable=True)
        message = aio_pika.Message(body=json.dumps({"url": url}).encode())
        await channel.default_exchange.publish(message, routing_key=queue.name)
        print(f"Published URL: {url}")

async def main():
    urls = [
        "https://via.placeholder.com/150",
        "https://via.placeholder.com/200",
        "https://via.placeholder.com/250"
        # Add more URLs as needed
    ]
    tasks = [publish_message(url) for url in urls]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
