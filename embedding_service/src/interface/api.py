"""
api.py

A minimal FastAPI application to expose a simple endpoint and provide Swagger UI.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Embedding Service API",
    description="API for health checks and administrative endpoints.",
    version="1.0.0"
)

@app.get("/health", summary="Health Check", description="Returns service health status.")
async def health_check():
    return {"status": "ok", "service": "embedding_service"}
