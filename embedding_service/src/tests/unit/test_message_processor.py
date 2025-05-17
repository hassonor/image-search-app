import contextlib
import os
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

root_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, root_path)

sys.modules.setdefault("elasticsearch", types.ModuleType("elasticsearch"))
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


pil_module = types.ModuleType("PIL")
pil_image_module = types.ModuleType("PIL.Image")
pil_image_module.new = lambda *args, **kwargs: dummy_image()
pil_module.Image = pil_image_module
sys.modules.setdefault("PIL", pil_module)
sys.modules.setdefault("PIL.Image", pil_image_module)


class Counter:
    def __init__(self, *_, **__):
        self._val = 0.0
        self._value = SimpleNamespace(get=lambda: self._val)

    def inc(self, amount: float = 1.0) -> None:
        self._val += amount


class Histogram:
    def __init__(self, *_, **__):
        self._val = 0.0
        self._value = SimpleNamespace(get=lambda: self._val)

    def observe(self, value: float) -> None:  # noqa: ARG002
        self._val += 1


prometheus_stub = types.ModuleType("prometheus_client")
prometheus_stub.Counter = Counter
prometheus_stub.Histogram = Histogram
prometheus_stub.start_http_server = MagicMock()
sys.modules["prometheus_client"] = prometheus_stub

from application.message_processor import process_message
from domain.embedding_service import EmbeddingService
from infrastructure.metrics import embedding_errors, embeddings_generated


class TestMessageProcessor(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        embeddings_generated._val = 0.0
        embedding_errors._val = 0.0

    async def test_process_message_success(self):
        with patch(
            "domain.embedding_service.EmbeddingService.__init__",
            lambda self, model_name="ViT-B/32": None,
        ):
            service = EmbeddingService(model_name="ViT-B/32")
        # Mock embedding generation
        with patch.object(
            service, "generate_embedding_from_image", return_value=[0.1, 0.2, 0.3]
        ):
            # Mock elasticsearch_client
            with patch("application.message_processor.elasticsearch_client") as mock_es:
                mock_es.index_embedding = AsyncMock(return_value=None)

                data = {
                    "image_id": 123,
                    "image_url": "http://example.com/img.jpg",
                    "image_path": "/path/to/img.jpg",
                }
                await process_message(data, service)

                # Check counters
                # Since it's a success, embeddings_generated should have incremented
                # embedding_errors should not increment
                self.assertEqual(embeddings_generated._value.get(), 1.0)
                self.assertEqual(embedding_errors._value.get(), 0.0)

    async def test_process_message_no_embedding(self):
        with patch(
            "domain.embedding_service.EmbeddingService.__init__",
            lambda self, model_name="ViT-B/32": None,
        ):
            service = EmbeddingService(model_name="ViT-B/32")
        # Mock embedding generation fails
        with patch.object(service, "generate_embedding_from_image", return_value=None):
            data = {
                "image_id": 123,
                "image_url": "http://example.com/img.jpg",
                "image_path": "/path/to/img.jpg",
            }
            await process_message(data, service)
            # embedding_errors should have incremented
            self.assertEqual(embedding_errors._value.get(), 1.0)
