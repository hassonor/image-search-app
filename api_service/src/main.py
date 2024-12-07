import asyncio

from elasticsearch import NotFoundError, RequestError
from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel
from typing import List

from metrics import start_metrics_server, queries_total, query_errors_total, query_latency
from config import settings
from embedding_service import EmbeddingService, logger
from src.elasticsearch_client import elasticsearch_client

app = FastAPI()
embedding_service = EmbeddingService()


class SearchResult(BaseModel):
    image_id: int
    image_url: str
    score: float


@app.on_event("startup")
async def startup_event():
    await elasticsearch_client.es.ping()
    start_metrics_server(port=settings.METRICS_PORT)
    logger.info("User Interface Service started.")


@app.on_event("shutdown")
async def shutdown_event():
    await elasticsearch_client.close()
    logger.info("User Interface Service shut down.")


@app.get("/get_image", response_model=List[SearchResult])
async def get_image(query_string: str = Query(..., min_length=1)):
    """
    Search for images based on the query string.
    """
    queries_total.inc()
    start_time = asyncio.get_event_loop().time()
    try:
        embedding = embedding_service.generate_embedding_from_text(query_string)
        if not embedding:
            raise HTTPException(status_code=500, detail="Failed to generate embedding for the query.")

        results = await elasticsearch_client.search_embeddings(embedding, top_k=5)
        search_time = asyncio.get_event_loop().time() - start_time
        query_latency.observe(search_time)

        if not results:
            raise HTTPException(status_code=404, detail="No images found matching the query.")

        response = [
            SearchResult(
                image_id=result["image_id"],
                image_url=result["image_url"],
                score=result["score"]
            )
            for result in results
        ]
        logger.info("Search query '%s' returned %d results.", query_string, len(response))
        return response
    except HTTPException as he:
        query_errors_total.inc()
        logger.error("HTTPException: %s", he.detail)
        raise he
    except NotFoundError as e:
        query_errors_total.inc()
        logger.error("Elasticsearch NotFoundError: %s", e)
        raise HTTPException(status_code=404, detail="Elasticsearch index not found.")

    except RequestError as e:
        query_errors_total.inc()
        logger.error("Elasticsearch RequestError: %s", e)
        raise HTTPException(status_code=400, detail="Bad request to Elasticsearch.")

    except Exception as e:
        query_errors_total.inc()
        logger.exception("Unexpected error during search: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/metrics")
async def metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
