import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
from domain.embedding_service import EmbeddingService
from application.message_processor import process_message
from infrastructure.metrics import embeddings_generated, embedding_errors

@pytest.mark.asyncio
async def test_process_message_success():
    service = EmbeddingService(model_name="ViT-B/32")

    # Mock embedding generation
    with patch.object(service, "generate_embedding_from_image", return_value=[0.1, 0.2, 0.3]):
        # Mock elasticsearch_client
        with patch("application.message_processor.elasticsearch_client") as mock_es:
            mock_es.index_embedding = AsyncMock(return_value=None)

            data = {"image_id": 123, "image_url": "http://example.com/img.jpg", "image_path": "/path/to/img.jpg"}
            await process_message(data, service)

            # Check counters
            # Since it's a success, embeddings_generated should have incremented
            # embedding_errors should not increment
            assert embeddings_generated._value.get() == 1.0
            assert embedding_errors._value.get() == 0.0

@pytest.mark.asyncio
async def test_process_message_no_embedding():
    service = EmbeddingService(model_name="ViT-B/32")

    # Mock embedding generation fails
    with patch.object(service, "generate_embedding_from_image", return_value=None):
        data = {"image_id": 123, "image_url": "http://example.com/img.jpg", "image_path": "/path/to/img.jpg"}
        await process_message(data, service)
        # embedding_errors should have incremented
        assert embedding_errors._value.get() == 1.0
