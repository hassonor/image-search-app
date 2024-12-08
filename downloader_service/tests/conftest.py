import pytest
from unittest.mock import AsyncMock
import sys
import os

root_path = os.path.join(os.path.dirname(__file__), '..', '..', 'downloader_service', 'src')
sys.path.insert(0, root_path)
@pytest.fixture
def mock_rabbitmq_client():
    mock_client = AsyncMock()
    mock_client.channel = AsyncMock()
    mock_client.channel.declare_queue = AsyncMock()
    mock_client.channel.default_exchange.publish = AsyncMock()
    return mock_client
