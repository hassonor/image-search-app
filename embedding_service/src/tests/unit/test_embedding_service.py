import contextlib
import os
import sys
import types
import unittest
from unittest.mock import MagicMock, patch

root_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, root_path)

torch_stub = types.ModuleType("torch")
torch_stub.cuda = types.SimpleNamespace(is_available=lambda: False)
torch_stub.no_grad = contextlib.nullcontext
sys.modules.setdefault("torch", torch_stub)
clip_stub = types.ModuleType("clip")
clip_stub.load = lambda model_name, device=None: (
    MagicMock(encode_image=MagicMock(return_value=MagicMock(shape=(1, 1)))),
    lambda x: x,
)
sys.modules.setdefault("clip", clip_stub)


def dummy_image():
    class Dummy:
        def convert(self, mode):
            return self

    return Dummy()


Image = type("Image", (), {"new": lambda *args, **kwargs: dummy_image()})
pil_module = types.ModuleType("PIL")
pil_image_module = types.ModuleType("PIL.Image")
pil_image_module.new = lambda *args, **kwargs: dummy_image()
pil_module.Image = pil_image_module
sys.modules.setdefault("PIL", pil_module)
sys.modules.setdefault("PIL.Image", pil_image_module)
prometheus_stub = types.ModuleType("prometheus_client")
prometheus_stub.Counter = MagicMock
prometheus_stub.Histogram = MagicMock
prometheus_stub.start_http_server = MagicMock
sys.modules.setdefault("prometheus_client", prometheus_stub)

from domain.embedding_service import EmbeddingService  # noqa: E402


class TestEmbeddingService(unittest.IsolatedAsyncioTestCase):
    async def test_generate_embedding_from_image(self):
        with patch(
            "domain.embedding_service.EmbeddingService.__init__",
            lambda self, model_name="ViT-B/32": None,
        ):
            service = EmbeddingService(model_name="ViT-B/32")
        with patch.object(
            service, "generate_embedding_from_image", return_value=[0.1, 0.2, 0.3]
        ):
            embedding = service.generate_embedding_from_image("path/to/image.jpg")
            self.assertEqual(embedding, [0.1, 0.2, 0.3])


class TestEmbeddingServiceError(unittest.TestCase):
    def test_generate_embedding_from_image_error(self):
        with patch(
            "domain.embedding_service.EmbeddingService.__init__",
            lambda self, model_name="ViT-B/32": None,
        ):
            service = EmbeddingService(model_name="ViT-B/32")
        with patch(
            "domain.embedding_service.Image.open", side_effect=Exception("fail")
        ) as mock_open, patch("domain.embedding_service.logger") as mock_logger:
            result = service.generate_embedding_from_image("bad.jpg")
            self.assertIsNone(result)
            mock_open.assert_called_once_with("bad.jpg")
            mock_logger.exception.assert_called_once()
