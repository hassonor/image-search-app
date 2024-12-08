import pytest
from unittest.mock import patch, AsyncMock

# Import from application layer directly, no longer from downloader_service.src
from application.messaging.callbacks import message_callback

@pytest.mark.asyncio
async def test_message_callback(mock_rabbitmq_client):
    """
    Test that the message_callback downloads the image and publishes embeddings.
    """
    mock_downloader = AsyncMock()
    mock_downloader.download_image = AsyncMock(return_value=(123, "/path/to/image.jpg"))

    # Patch publish_embeddings where it's actually used in callbacks.py
    with patch("application.messaging.callbacks.publish_embeddings", new_callable=AsyncMock) as mock_publish:
        url = "http://example.com/image.jpg"
        await message_callback(url, mock_downloader)

        mock_downloader.download_image.assert_awaited_once_with(url)
        mock_publish.assert_awaited_once_with(123, url, "/path/to/image.jpg")
