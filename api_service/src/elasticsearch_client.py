import logging
from elasticsearch import AsyncElasticsearch, exceptions
from config import settings

logger = logging.getLogger(__name__)


class ElasticsearchClient:
    """Elasticsearch client for searching embeddings."""

    def __init__(self):
        self.es = AsyncElasticsearch(
            hosts=[f"http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"],
            timeout=30,
            max_retries=10,
            retry_on_timeout=True
        )

    async def search_embeddings(self, embedding: list, top_k: int = 5):
        """Search for similar embeddings in Elasticsearch."""
        try:
            query = {
                "size": top_k,
                "query": {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": embedding}
                        }
                    }
                }
            }
            response = await self.es.search(index=settings.ELASTICSEARCH_INDEX, body=query)
            hits = response['hits']['hits']
            results = []
            for hit in hits:
                score = hit['_score']
                source = hit['_source']

                results.append({
                    "image_id": source.get("image_id"),
                    "image_url": source.get("image_url"),
                    "image_path": source.get("image_path"),
                    "score": score
                })
            logger.debug("Elasticsearch search returned %d results.", len(results))
            return results
        except exceptions.NotFoundError as e:
            logger.exception("Elasticsearch search failed: Index not found. %s", e)
            return []
        except exceptions.RequestError as e:
            logger.exception("Elasticsearch request failed: %s", e)
            return []
        except Exception as e:
            logger.exception("An unexpected error occurred during search: %s", e)
            return []

    async def close(self):
        """Close the Elasticsearch connection."""
        await self.es.close()
        logger.info("Elasticsearch connection closed.")


elasticsearch_client = ElasticsearchClient()
