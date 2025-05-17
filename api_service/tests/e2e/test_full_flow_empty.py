import os
import sys
import types
import unittest
import asyncio
import importlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from application.pagination import paginate_results
from application.models import SearchResult, FullSearchResponse

class TestFullFlowEmpty(unittest.TestCase):
    def test_full_flow_empty(self):
        sys.modules.pop('elasticsearch', None)
        es_module = types.ModuleType('elasticsearch')

        class AsyncElasticsearch:
            def __init__(self, *args, **kwargs):
                pass

            async def search(self, index, body):
                return {'hits': {'hits': []}}

            async def close(self):
                pass

        es_module.AsyncElasticsearch = AsyncElasticsearch
        es_module.exceptions = types.SimpleNamespace(NotFoundError=Exception, RequestError=Exception)
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
        response = FullSearchResponse(query='empty', results=[SearchResult(**r) for r in paged])
        self.assertEqual(response.query, 'empty')
        self.assertEqual(len(response.results), 0)

if __name__ == '__main__':
    unittest.main()
