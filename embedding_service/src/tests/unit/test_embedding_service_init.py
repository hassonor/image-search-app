import contextlib
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

root_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, root_path)

from domain.embedding_service import EmbeddingService


class DummyTensor:
    def unsqueeze(self, _):
        return self

    def to(self, _):
        return self


class TestEmbeddingServiceInit(unittest.TestCase):
    def test_init_sets_dimension_and_device(self):
        embedding = MagicMock()
        embedding.shape = (1, 123)
        model = MagicMock(encode_image=MagicMock(return_value=embedding))
        preprocess = MagicMock(return_value=DummyTensor())
        with patch(
            "domain.embedding_service.clip.load", return_value=(model, preprocess)
        ) as load_mock, patch(
            "domain.embedding_service.Image.new", return_value="img"
        ) as image_new, patch(
            "domain.embedding_service.torch.cuda.is_available", return_value=False
        ), patch(
            "domain.embedding_service.torch.no_grad", lambda: contextlib.nullcontext()
        ):
            service = EmbeddingService(model_name="dummy")
            self.assertEqual(service.dimension, 123)
            self.assertEqual(service.device, "cpu")
            load_mock.assert_called_once_with("dummy", device="cpu")
            image_new.assert_called_once()
