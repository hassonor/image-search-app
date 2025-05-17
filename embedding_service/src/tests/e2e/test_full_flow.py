import contextlib
import os
import sys
import types
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

root_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, root_path)
es_stub = types.ModuleType("elasticsearch")
es_stub.AsyncElasticsearch = MagicMock
es_stub.exceptions = types.SimpleNamespace(NotFoundError=Exception)
sys.modules.setdefault("elasticsearch", es_stub)
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


class TestEmbeddingE2E(unittest.IsolatedAsyncioTestCase):
    async def test_full_flow(self):
        with patch(
            "domain.embedding_service.EmbeddingService.__init__",
            lambda self, model_name="ViT-B/32": None,
        ):
            service = EmbeddingService(model_name="ViT-B/32")
        with patch.object(
            service, "generate_embedding_from_image", return_value=[0.1]
        ) as mock_gen, patch(
            "application.message_processor.elasticsearch_client"
        ) as mock_es:
            mock_es.index_embedding = AsyncMock(return_value=None)
            data = {"image_id": 1, "image_url": "u", "image_path": "p"}
            await process_message(data, service)
            mock_gen.assert_called_once_with("p")
            mock_es.index_embedding.assert_awaited_once()
