import pytest
from unittest.mock import AsyncMock
from downloader_service.src.startup import retry_connection

@pytest.mark.asyncio
async def test_retry_connection_success():
    mock_connect = AsyncMock()
    await retry_connection(mock_connect, max_retries=2, delay=0.1, name="TestService")
    mock_connect.assert_awaited_once()

@pytest.mark.asyncio
async def test_retry_connection_failure():
    mock_connect = AsyncMock(side_effect=Exception("Connection failed"))
    with pytest.raises(ConnectionError):
        await retry_connection(mock_connect, max_retries=2, delay=0.1, name="FailService")
    assert mock_connect.await_count == 2
