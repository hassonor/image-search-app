import os
import sys
import types
import importlib
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock

# Stub httpx before importing TestClient to avoid missing dependency
sys.modules.setdefault('httpx', types.ModuleType('httpx'))

root_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
sys.path.insert(0, os.path.abspath(root_path))


class Counter:
    def __init__(self):
        self.calls = 0
    def inc(self):
        self.calls += 1

class Histogram:
    def __init__(self):
        self.values = []
    def observe(self, value):
        self.values.append(value)


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        embed_service = MagicMock()
        embed_service.generate_embedding_from_text = MagicMock(return_value=[0.1, 0.2])
        embed_module = types.ModuleType('domain.embedding_service')
        embed_module.EmbeddingService = lambda: embed_service
        sys.modules['domain.embedding_service'] = embed_module

        es_client = types.SimpleNamespace(
            search_embeddings=AsyncMock(return_value=[{'image_id': 1, 'image_url': 'u', 'image_path': 'p', 'score': 0.9}]),
            close=AsyncMock()
        )
        es_module = types.ModuleType('infrastructure.elasticsearch_client')
        es_module.elasticsearch_client = es_client
        sys.modules['infrastructure.elasticsearch_client'] = es_module

        metrics_module = types.ModuleType('infrastructure.metrics')
        metrics_module.queries_total = Counter()
        metrics_module.query_errors_total = Counter()
        metrics_module.query_latency = Histogram()
        sys.modules['infrastructure.metrics'] = metrics_module

        prom_module = types.ModuleType('prometheus_client')
        prom_module.generate_latest = lambda: b'metrics'
        prom_module.CONTENT_TYPE_LATEST = 'text/plain'
        sys.modules['prometheus_client'] = prom_module

        # Stub httpx required by FastAPI TestClient
        httpx_module = types.ModuleType('httpx')
        sys.modules.setdefault('httpx', httpx_module)

        import interface.api as api_module
        importlib.reload(api_module)
        cls.api = api_module
        cls.metrics = metrics_module
        cls.embed_service = api_module.embedding_service

    def test_health_endpoint(self):
        response = asyncio.run(self.api.health())
        self.assertEqual(response, {'status': 'ok', 'service': 'api_server'})

    def test_get_image_success(self):
        self.embed_service.generate_embedding_from_text.return_value = [0.1, 0.2]
        before = self.metrics.queries_total.calls
        err_before = self.metrics.query_errors_total.calls
        data = asyncio.run(self.api.get_image(query_string='hi', page=1, size=1))
        self.assertEqual(data.query, 'hi')
        self.assertEqual(len(data.results), 1)
        self.assertEqual(data.results[0].image_id, 1)
        self.assertEqual(self.metrics.queries_total.calls, before + 1)
        self.assertEqual(self.metrics.query_errors_total.calls, err_before)

    def test_get_image_embedding_failure(self):
        self.embed_service.generate_embedding_from_text.return_value = []
        before = self.metrics.query_errors_total.calls
        with self.assertRaises(self.api.HTTPException):
            asyncio.run(self.api.get_image(query_string='bad', page=1, size=1))
        self.assertEqual(self.metrics.query_errors_total.calls, before + 1)


if __name__ == '__main__':
    unittest.main()
