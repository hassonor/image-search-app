import os
import sys
import unittest
import types
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import importlib

class TestElasticsearchClient(unittest.IsolatedAsyncioTestCase):
    async def test_search_embeddings(self):
        sys.modules.pop('elasticsearch', None)
        es_module = types.ModuleType('elasticsearch')

        class AsyncElasticsearch:
            def __init__(self, *args, **kwargs):
                pass

            async def search(self, index, body):
                return {
                    'hits': {
                        'hits': [
                            {'_score': 1.0, '_source': {'image_id': 1, 'image_url': 'u', 'image_path': 'p'}}
                        ]
                    }
                }

            async def close(self):
                pass

        es_module.AsyncElasticsearch = AsyncElasticsearch

        class exceptions:
            class NotFoundError(Exception):
                pass

            class RequestError(Exception):
                pass

        es_module.exceptions = exceptions
        sys.modules['elasticsearch'] = es_module

        import infrastructure.elasticsearch_client as es_client_module
        importlib.reload(es_client_module)
        client = es_client_module.ElasticsearchClient()
        results = await client.search_embeddings([0.1, 0.2], top_k=1)
        await client.close()
        self.assertEqual(results[0]['image_id'], 1)

if __name__ == '__main__':
    unittest.main()
