"""
api.py

A minimal FastAPI application exposing a health check endpoint and Swagger UI.
"""

from fastapi import FastAPI

app = FastAPI(
    title="Downloader Service API",
    description="API for health checks and administrative endpoints.",
    version="1.0.0",
)


@app.get("/health", summary="Health Check", description="Returns service health status.")
async def health_check():
    """
    Health check endpoint to verify service is up and running.
    Returns status and service name.
    """
    return {"status": "ok", "service": "downloader_service"}
