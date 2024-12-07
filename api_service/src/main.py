import asyncio

from elasticsearch import NotFoundError, RequestError
from fastapi import FastAPI, HTTPException, Query, Response
from pydantic import BaseModel
from typing import List

from starlette.middleware.cors import CORSMiddleware

from pagination import paginate_results
from metrics import start_metrics_server, queries_total, query_errors_total, query_latency
from config import settings
from embedding_service import EmbeddingService, logger
from elasticsearch_client import elasticsearch_client

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_service = EmbeddingService()


class SearchResult(BaseModel):
    image_id: int
    image_url: str
    score: float


@app.on_event("startup")
async def startup_event():
    # Check Elasticsearch connectivity by a no-op ping
    await elasticsearch_client.es.ping()
    start_metrics_server(port=settings.METRICS_PORT)
    logger.info("API Service started.")


@app.on_event("shutdown")
async def shutdown_event():
    await elasticsearch_client.close()
    logger.info("User Interface Service shut down.")


@app.get("/get_image", response_model=List[SearchResult])
async def get_image(
        query_string: str = Query(..., min_length=1),
        page: int = Query(1, ge=1),
        size: int = Query(20, ge=1, le=100),
):
    """
    Search for images based on the query string with pagination.
    Returns a list of SearchResult objects.
    """
    queries_total.inc()
    start_time = asyncio.get_event_loop().time()

    try:
        embedding = embedding_service.generate_embedding_from_text(query_string)
        if not embedding:
            raise HTTPException(
                status_code=500, detail="Failed to generate embedding for the query."
            )

        # Retrieve top_k results based on page and size
        top_k = page * size
        results = await elasticsearch_client.search_embeddings(embedding, top_k=top_k)
        paged_results = paginate_results(results, page=page, size=size)

        search_time = asyncio.get_event_loop().time() - start_time
        query_latency.observe(search_time)

        if not paged_results:
            # Return empty list with status 200 if no matches
            return []

        logger.info("Search query '%s' returned %d results (page %d, size %d).",
                    query_string, len(paged_results), page, size)
        return [SearchResult(**res) for res in paged_results]
    except HTTPException as he:
        query_errors_total.inc()
        logger.error("HTTPException: %s", he.detail)
        raise he
    except NotFoundError as e:
        query_errors_total.inc()
        logger.error("Elasticsearch NotFoundError: %s", e)
        raise HTTPException(status_code=400, detail="Elasticsearch index not found.")

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
