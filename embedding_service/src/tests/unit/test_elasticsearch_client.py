import importlib
import os
import sys
import types
import unittest

root_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, root_path)


class AsyncIndices:
    def __init__(self, parent):
        self.parent = parent

    async def exists(self, index):
        return self.parent.exists_return

    async def create(self, index, body):
        self.parent.created = (index, body)


class FakeAsyncElasticsearch:
    def __init__(self, *args, **kwargs):
        self.indices = AsyncIndices(self)
        self.indexed = None
        self.closed = False
        self.exists_return = False
        self.created = None

    async def index(self, index, body):
        self.indexed = (index, body)

    async def close(self):
        self.closed = True


class exceptions:
    class ElasticsearchException(Exception):
        pass


class TestElasticsearchClient(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.es_module = types.ModuleType("elasticsearch")
        self.es_module.AsyncElasticsearch = FakeAsyncElasticsearch
        self.es_module.exceptions = exceptions
        sys.modules["elasticsearch"] = self.es_module
        import infrastructure.elasticsearch_client as es_mod

        importlib.reload(es_mod)
        self.es_client_module = es_mod
        self.client = es_mod.ElasticsearchClient()

    def tearDown(self):
        sys.modules.pop("elasticsearch", None)
        sys.modules.pop("infrastructure.elasticsearch_client", None)

    async def test_create_index_creates_when_missing(self):
        self.client.es.exists_return = False
        with self.assertLogs("infrastructure.elasticsearch_client", level="INFO") as cm:
            await self.client.create_index()
        self.assertIsNotNone(self.client.es.created)
        self.assertIn("Created Elasticsearch index", cm.output[0])

    async def test_index_embedding_sends_correct_document(self):
        await self.client.index_embedding(
            image_id=1,
            image_url="url",
            image_path="path",
            embedding=[0.1, 0.2],
        )
        expected_doc = {
            "image_id": 1,
            "image_url": "url",
            "image_path": "path",
            "embedding": [0.1, 0.2],
        }
        self.assertEqual(
            self.client.es.indexed,
            (self.es_client_module.settings.ELASTICSEARCH_INDEX, expected_doc),
        )

    async def test_close_awaits_es_close(self):
        await self.client.close()
        self.assertTrue(self.client.es.closed)

    async def test_elasticsearch_exception_propagates(self):
        async def raise_exception(*args, **kwargs):
            raise exceptions.ElasticsearchException("boom")

        self.client.es.indices.exists = raise_exception
        with self.assertRaises(exceptions.ElasticsearchException):
            await self.client.create_index()
