import pytest
from unittest.mock import patch, AsyncMock
from downloader_service.src.messaging.publishers import process_and_publish_chunk, publish_embeddings
from downloader_service.src.messaging.callbacks import message_callback


@pytest.mark.asyncio
async def test_process_and_publish_chunk():
    with patch("downloader_service.src.messaging.publishers.redis_client.check_urls_batch",
               return_value=["http://example.com/img.jpg"]):
        mock_channel = AsyncMock()
        with patch("downloader_service.src.messaging.publishers.rabbitmq_client.channel", mock_channel):
            await process_and_publish_chunk(["http://example.com/img.jpg"])
            mock_channel.default_exchange.publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_publish_embeddings():
    with patch("downloader_service.src.messaging.publishers.rabbitmq_client.publish",
               new_callable=AsyncMock) as mock_publish:
        await publish_embeddings(123, "http://example.com/img.jpg", "/local/path.jpg")
        mock_publish.assert_awaited_once()


@pytest.mark.asyncio
async def test_message_callback(mock_rabbitmq_client):
    mock_downloader = AsyncMock()
    mock_downloader.download_image = AsyncMock(return_value=(123, "/path/to/image.jpg"))

    # Patch the publish_embeddings function exactly as it is referenced in callbacks.py
    with patch("downloader_service.src.messaging.callbacks.publish_embeddings", new_callable=AsyncMock) as mock_publish:
        url = "http://example.com/image.jpg"
        await message_callback(url, mock_downloader)
        mock_downloader.download_image.assert_awaited_once_with(url)
        mock_publish.assert_awaited_once_with(123, url, "/path/to/image.jpg")