"""
main.py

Main entry point for the API Service.

Orchestrates:
- Elasticsearch connectivity check
- Starting metrics server
- Shutting down resources
- Running FastAPI application (handled by uvicorn)
"""

import asyncio
import signal
from infrastructure.logging_config import logger
from infrastructure.metrics import start_metrics_server
from infrastructure.config import settings
from infrastructure.elasticsearch_client import elasticsearch_client
from application.shutdown import shutdown


# The FastAPI app and routes are defined in interface/api.py
# Uvicorn or another ASGI server will run `main:app` as needed.

async def startup_event():
    """
    Startup event: Check Elasticsearch connectivity and start metrics server.
    """
    await elasticsearch_client.es.ping()
    start_metrics_server(port=settings.METRICS_PORT)
    logger.info("API Service started.")


async def shutdown_event():
    """
    Shutdown event: Close Elasticsearch client.
    """
    await elasticsearch_client.close()
    logger.info("API Service shut down.")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)
