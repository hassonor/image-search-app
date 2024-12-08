import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
from domain.embedding_service import EmbeddingService

@pytest.mark.asyncio
async def test_generate_embedding_from_image():
    service = EmbeddingService(model_name="ViT-B/32")

    with patch("PIL.Image.open") as mock_open, patch.object(service.model, "encode_image") as mock_encode:
        # Return a real PIL image
        mock_open.return_value = Image.new('RGB', (224, 224))

        mock_encode.return_value = MagicMock()
        mock_encode.return_value.__truediv__.return_value = mock_encode.return_value
        mock_encode.return_value.norm.return_value = mock_encode.return_value
        # Make sure to return a 2D list for tolist()
        mock_encode.return_value.cpu.return_value.numpy.return_value.tolist.return_value = [[0.1, 0.2, 0.3]]

        embedding = service.generate_embedding_from_image("path/to/image.jpg")
        assert embedding == [0.1, 0.2, 0.3]
