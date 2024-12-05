import os
import pytest
import json
from unittest.mock import patch, MagicMock
from embedding_service.embedding_service import EmbeddingGenerator, main

@pytest.fixture
def mock_embedding_generator():
    """
    Fixture to mock the EmbeddingGenerator class with patched CLIPModel and CLIPProcessor.
    """
    with patch("embedding_service.embedding_service.CLIPModel") as MockModel, \
         patch("embedding_service.embedding_service.CLIPProcessor") as MockProcessor:
        MockModel.from_pretrained.return_value = MagicMock()
        MockProcessor.from_pretrained.return_value = MagicMock()
        yield EmbeddingGenerator()

def test_generate_embeddings_for_image(mock_embedding_generator):
    """
    Test embedding generation for a single image.
    """

    # Final expected Python list result
    tolist_result = [0.1, 0.2, 0.3]

    # Mock the chain of method calls on the embeddings tensor
    cpu_mock = MagicMock()
    # .tolist() should return the real list, not a mock
    cpu_mock.tolist.return_value = tolist_result

    squeeze_mock = MagicMock()
    # .cpu() returns cpu_mock
    squeeze_mock.cpu.return_value = cpu_mock

    mock_feat = MagicMock()
    # .squeeze() returns squeeze_mock
    mock_feat.squeeze.return_value = squeeze_mock

    # get_image_features returns mock_feat
    mock_embedding_generator.model.get_image_features.return_value = mock_feat

    # Mock Image.open so we don't need an actual image file
    with patch("embedding_service.embedding_service.Image.open") as mock_image:
        mock_image.return_value.convert.return_value = MagicMock()

        embedding = mock_embedding_generator.generate_embeddings_for_image("test.jpg")
        assert embedding == tolist_result, "Embedding output should match mocked data"


def test_generate_all_embeddings(mock_embedding_generator, tmp_path):
    """
    Test embedding generation for multiple images.
    """
    mock_images = ["image1.jpg", "image2.png"]
    images_dir = tmp_path / "images"
    os.makedirs(images_dir, exist_ok=True)
    for img in mock_images:
        # Just write some dummy content; we will mock the image loading anyway.
        with open(images_dir / img, "w") as f:
            f.write("mock data")

    # Patch IMAGES_DIR to our temporary images directory
    with patch("embedding_service.embedding_service.IMAGES_DIR", images_dir):
        # Mock generate_embeddings_for_image to return a consistent embedding
        with patch.object(mock_embedding_generator, "generate_embeddings_for_image", return_value=[0.1, 0.2, 0.3]):
            embeddings = mock_embedding_generator.generate_all_embeddings()
            assert len(embeddings) == len(mock_images), "All images should generate embeddings"
            assert "image1.jpg" in embeddings, "image1.jpg should be in the results"
            assert embeddings["image1.jpg"] == [0.1, 0.2, 0.3], "Embedding should match mock data"

def test_main(monkeypatch, tmp_path, mock_embedding_generator):
    """
    Test the main function to ensure embeddings are generated and saved.
    """
    images_dir = tmp_path / "images"
    mock_output_file = tmp_path / "embeddings.json"
    os.makedirs(images_dir, exist_ok=True)
    with open(images_dir / "image1.jpg", "w") as f:
        f.write("mock data")

    # Patch constants to point to our temporary directories
    monkeypatch.setattr("embedding_service.embedding_service.IMAGES_DIR", images_dir)
    monkeypatch.setattr("embedding_service.embedding_service.OUTPUT_FILE", mock_output_file)

    # Mock generate_all_embeddings so main writes embeddings.json
    with patch("embedding_service.embedding_service.EmbeddingGenerator.generate_all_embeddings",
               return_value={"image1.jpg": [0.1, 0.2, 0.3]}):
        main()

    with open(mock_output_file, "r") as f:
        data = json.load(f)
    assert "image1.jpg" in data, "Output file should contain image embeddings"
    assert data["image1.jpg"] == [0.1, 0.2, 0.3], "Embeddings should match mock data"
