import logging
from elasticsearch import AsyncElasticsearch, exceptions
from config import settings

logger = logging.getLogger(__name__)


class ElasticsearchClient:
    """Elasticsearch client for indexing and searching embeddings."""

    def __init__(self):
        self.es = AsyncElasticsearch(
            hosts=[f"http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"],
            timeout=30,
            max_retries=10,
            retry_on_timeout=True
        )

    async def create_index(self):
        """Create an index with vector capabilities if it doesn't exist."""
        try:
            exists = await self.es.indices.exists(index=settings.ELASTICSEARCH_INDEX)
            if not exists:
                index_body = {
                    "mappings": {
                        "properties": {
                            "image_id": {"type": "integer"},
                            "image_path": {"type": "text"},
                            "embedding": {
                                "type": "dense_vector",
                                "dims": 512  # Adjust based on your embedding model
                            }
                        }
                    }
                }
                await self.es.indices.create(index=settings.ELASTICSEARCH_INDEX, body=index_body)
                logger.info("Created Elasticsearch index: %s", settings.ELASTICSEARCH_INDEX)
            else:
                logger.info("Elasticsearch index already exists: %s", settings.ELASTICSEARCH_INDEX)
        except exceptions.ElasticsearchException as e:
            logger.exception("Failed to create or verify Elasticsearch index: %s", e)
            raise

    async def index_embedding(self, image_id: int, image_url: str,image_path:str, embedding: list):
        """Index a single embedding into Elasticsearch."""
        try:
            doc = {
                "image_id": image_id,
                "image_url": image_url,
                "image_path": image_path,
                "embedding": embedding
            }
            await self.es.index(index=settings.ELASTICSEARCH_INDEX, body=doc)
            logger.debug("Indexed embedding for image_id: %s", image_id)
        except exceptions.ElasticsearchException as e:
            logger.exception("Failed to index embedding for image_id %s: %s", image_id, e)
            raise

    async def close(self):
        """Close the Elasticsearch connection."""
        await self.es.close()
        logger.info("Elasticsearch connection closed.")


elasticsearch_client = ElasticsearchClient()
