import os
import sys
import types
import contextlib
import importlib
import unittest
from unittest.mock import MagicMock

root_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
sys.path.insert(0, os.path.abspath(root_path))


class FakeTensor:
    def __init__(self, arr):
        self.arr = list(arr)
        self.shape = (1, len(self.arr))

    def to(self, device):
        return self

    def norm(self, dim=-1, keepdim=True):
        import math
        return FakeTensor([math.sqrt(sum(x * x for x in self.arr))])

    def __truediv__(self, other):
        val = other.arr[0] if isinstance(other, FakeTensor) else other
        return FakeTensor([x / val for x in self.arr])

    def cpu(self):
        return self

    def numpy(self):
        return self

    def tolist(self):
        return [self.arr]


def setup_modules(mock_model):
    clip_module = types.ModuleType('clip')
    clip_module.load = lambda model_name, device=None: (mock_model, None)
    clip_module.tokenize = lambda text: FakeTensor([0])
    sys.modules['clip'] = clip_module

    torch_module = types.ModuleType('torch')
    torch_module.cuda = types.SimpleNamespace(is_available=lambda: False)
    torch_module.no_grad = contextlib.nullcontext
    sys.modules['torch'] = torch_module


class TestEmbeddingService(unittest.TestCase):
    def tearDown(self):
        sys.modules.pop('clip', None)
        sys.modules.pop('torch', None)
        sys.modules.pop('domain.embedding_service', None)

    def test_generate_embedding_success(self):
        mock_model = MagicMock()
        mock_model.encode_text.return_value = FakeTensor([1.0, 0.0])
        setup_modules(mock_model)
        import domain.embedding_service as emb_mod
        importlib.reload(emb_mod)
        service = emb_mod.EmbeddingService()
        embedding = service.generate_embedding_from_text('hi')
        self.assertEqual(embedding, [1.0, 0.0])

    def test_generate_embedding_failure(self):
        mock_model = MagicMock()
        mock_model.encode_text.return_value = FakeTensor([1.0])
        setup_modules(mock_model)
        import domain.embedding_service as emb_mod
        importlib.reload(emb_mod)
        service = emb_mod.EmbeddingService()
        service.model.encode_text.side_effect = Exception('fail')
        embedding = service.generate_embedding_from_text('hi')
        self.assertEqual(embedding, [])


if __name__ == '__main__':
    unittest.main()

