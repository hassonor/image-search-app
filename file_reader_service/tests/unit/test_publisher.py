import pytest
from unittest.mock import patch, AsyncMock
from file_reader_service.src.application.publisher import process_and_publish_chunk
from domain.file_reader_service import FileReaderService

@pytest.mark.asyncio
async def test_process_and_publish_chunk():
    mock_channel = AsyncMock()
    # Patch the rabbitmq_client.channel as before
    with patch("file_reader_service.src.application.publisher.rabbitmq_client.channel", mock_channel):
        # Use a mock redis_client and configure it to return a URL
        mock_redis_client = AsyncMock()
        mock_redis_client.check_urls_batch.return_value = ["http://example.com/img.jpg"]

        # Create the service with the mock_redis_client
        service = FileReaderService(redis_client=mock_redis_client)

        # Call process_and_publish_chunk with both arguments
        await process_and_publish_chunk(["http://example.com/img.jpg"], service)

        # Verify that a message was published
        mock_channel.default_exchange.publish.assert_awaited_once()
