import pytest
from unittest.mock import AsyncMock
import sys
import os

# Add the embedding service src directory to the Python path for module imports.
root_path = os.path.join(os.path.dirname(__file__), "..", "..", "embedding_service", "src")
sys.path.insert(0, root_path)


@pytest.fixture
def mock_rabbitmq_client():
    """
    Provides a mock RabbitMQ client fixture for testing.

    This fixture returns an AsyncMock client object with a mocked channel and
    queue declaration methods. It can be used in unit tests that require a
    RabbitMQ client without connecting to an actual RabbitMQ instance.
    """
    mock_client = AsyncMock()
    mock_client.channel = AsyncMock()
    mock_client.channel.declare_queue = AsyncMock()
    mock_client.channel.default_exchange.publish = AsyncMock()
    return mock_client
