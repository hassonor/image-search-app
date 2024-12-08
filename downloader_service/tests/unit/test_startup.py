import pytest
from unittest.mock import AsyncMock
from application.retry import retry_connection

@pytest.mark.asyncio
async def test_retry_connection_success():
    """
    Test successful connection on the first try with retry_connection.
    """
    mock_connect = AsyncMock()
    await retry_connection(mock_connect, max_retries=2, delay=0.1, name="TestService")
    mock_connect.assert_awaited_once()

@pytest.mark.asyncio
async def test_retry_connection_failure():
    """
    Test that retry_connection raises ConnectionError after max_retries failures.
    """
    mock_connect = AsyncMock(side_effect=Exception("Connection failed"))
    with pytest.raises(ConnectionError):
        await retry_connection(mock_connect, max_retries=2, delay=0.1, name="FailService")
    assert mock_connect.await_count == 2
