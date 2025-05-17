import os
import sys
import types
import importlib
import unittest
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

class TestElasticsearchClientErrors(unittest.IsolatedAsyncioTestCase):
    async def test_not_found_returns_empty(self):
        es_module = types.ModuleType('elasticsearch')

        class NotFoundError(Exception):
            pass

        class RequestError(Exception):
            pass

        class AsyncElasticsearch:
            def __init__(self, *args, **kwargs):
                pass

            async def search(self, index, body):
                raise NotFoundError('no index')

            async def close(self):
                pass

        es_module.AsyncElasticsearch = AsyncElasticsearch
        es_module.exceptions = types.SimpleNamespace(NotFoundError=NotFoundError, RequestError=RequestError)
        sys.modules['elasticsearch'] = es_module

        import infrastructure.elasticsearch_client as es_client_module
        importlib.reload(es_client_module)

        client = es_client_module.ElasticsearchClient()
        results = await client.search_embeddings([0.1], top_k=1)
        await client.close()
        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
