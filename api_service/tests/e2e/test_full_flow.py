import os
import sys
import unittest
import types
import asyncio

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
import importlib
from application.pagination import paginate_results
from application.models import SearchResult, FullSearchResponse

class TestFullFlow(unittest.TestCase):
    def test_full_flow(self):
        sys.modules.pop('elasticsearch', None)
        es_module = types.ModuleType('elasticsearch')

        class AsyncElasticsearch:
            def __init__(self, *args, **kwargs):
                pass

            async def search(self, index, body):
                return {
                    'hits': {
                        'hits': [
                            {'_score': 0.9, '_source': {'image_id': 2, 'image_url': 'url', 'image_path': 'path'}}
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
        async def run_flow():
            client = es_client_module.ElasticsearchClient()
            results = await client.search_embeddings([0.1], top_k=1)
            await client.close()
            paged = paginate_results(results, page=1, size=1)
            return paged
        paged = asyncio.run(run_flow())
        response = FullSearchResponse(
            query='test',
            results=[SearchResult(**r) for r in paged]
        )
        self.assertEqual(response.query, 'test')
        self.assertEqual(len(response.results), 1)
        self.assertEqual(response.results[0].image_id, 2)

if __name__ == '__main__':
    unittest.main()
