import pytest
from unittest.mock import AsyncMock
import sys
import os

# Set PYTHONPATH so that tests can find the modules in src easily.
root_path = os.path.join(os.path.dirname(__file__), "..", "..", "src")
sys.path.insert(0, root_path)

@pytest.fixture
def mock_rabbitmq_client():
    """
    Provides a mock RabbitMQ client fixture for testing.
    Mocks the channel, queue declaration, and publish methods.
    """
    mock_client = AsyncMock()
    mock_client.channel = AsyncMock()
    mock_client.channel.declare_queue = AsyncMock()
    mock_client.channel.default_exchange.publish = AsyncMock()
    return mock_client
