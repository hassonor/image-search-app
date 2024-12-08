"""
interface/api.py

FastAPI application defining the API endpoints, including a health check.
"""

from fastapi import FastAPI, Query, HTTPException, Response
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import asyncio
import logging

from infrastructure.metrics import queries_total, query_errors_total, query_latency
from application.pagination import paginate_results
from application.models import SearchResult, FullSearchResponse  # Import FullSearchResponse
from domain.embedding_service import EmbeddingService
from infrastructure.elasticsearch_client import elasticsearch_client


logger = logging.getLogger(__name__)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

embedding_service = EmbeddingService()

@app.get("/health", summary="Health Check", description="Return service health status.")
async def health():
    """
    Health check endpoint to verify the API service is running.
    """
    return {"status": "ok", "service": "api_server"}


@app.get("/get_image", response_model=FullSearchResponse)
async def get_image(
    query_string: str = Query(..., min_length=1),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
):
    """
    Search for images based on the query string with pagination.
    Returns a response containing the query and a list of SearchResult objects.
    """
    queries_total.inc()
    start_time = asyncio.get_event_loop().time()

    try:
        embedding = embedding_service.generate_embedding_from_text(query_string)
        if not embedding:
            raise HTTPException(
                status_code=500, detail="Failed to generate embedding for the query."
            )

        top_k = page * size
        results = await elasticsearch_client.search_embeddings(embedding, top_k=top_k)
        paged_results = paginate_results(results, page=page, size=size)

        search_time = asyncio.get_event_loop().time() - start_time
        query_latency.observe(search_time)

        if not paged_results:
            # Return empty results but still include the query
            return FullSearchResponse(query=query_string, results=[])

        logger.info(
            "Search query '%s' returned %d results (page %d, size %d).",
            query_string, len(paged_results), page, size
        )
        return FullSearchResponse(
            query=query_string,
            results=[SearchResult(**res) for res in paged_results]
        )

    except HTTPException as he:
        query_errors_total.inc()
        logger.error("HTTPException: %s", he.detail)
        raise he
    except Exception as e:
        query_errors_total.inc()
        logger.exception("Unexpected error during search: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/metrics")
async def metrics():
    """
    Endpoint to expose Prometheus metrics.
    """
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
