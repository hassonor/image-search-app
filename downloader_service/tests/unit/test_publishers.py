import pytest
from unittest.mock import patch, AsyncMock
from application.messaging.publishers import process_and_publish_chunk, publish_embeddings
from application.messaging.callbacks import message_callback

@pytest.mark.asyncio
async def test_process_and_publish_chunk():
    """
    Test that process_and_publish_chunk filters and publishes new URLs to the download queue.
    """
    with patch("application.messaging.publishers.redis_client.check_urls_batch", return_value=["http://example.com/img.jpg"]):
        mock_channel = AsyncMock()
        with patch("application.messaging.publishers.rabbitmq_client.channel", mock_channel):
            await process_and_publish_chunk(["http://example.com/img.jpg"])
            mock_channel.default_exchange.publish.assert_awaited_once()

@pytest.mark.asyncio
async def test_publish_embeddings():
    """
    Test that publish_embeddings publishes the correct message to the embedding queue.
    """
    with patch("application.messaging.publishers.rabbitmq_client.publish", new_callable=AsyncMock) as mock_publish:
        await publish_embeddings(123, "http://example.com/img.jpg", "/local/path.jpg")
        mock_publish.assert_awaited_once()

@pytest.mark.asyncio
async def test_message_callback(mock_rabbitmq_client):
    """
    Test message_callback logic integrated with publish_embeddings mock.
    """
    mock_downloader = AsyncMock()
    mock_downloader.download_image = AsyncMock(return_value=(123, "/path/to/image.jpg"))

    # Patch publish_embeddings in callbacks
    with patch("application.messaging.callbacks.publish_embeddings", new_callable=AsyncMock) as mock_publish:
        url = "http://example.com/image.jpg"
        await message_callback(url, mock_downloader)
        mock_downloader.download_image.assert_awaited_once_with(url)
        mock_publish.assert_awaited_once_with(123, url, "/path/to/image.jpg")
