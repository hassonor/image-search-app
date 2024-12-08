"""
server_runner.py

Responsible for running the FastAPI server for swagger/UI endpoints in a background task.
"""

import uvicorn
import logging
from api import app

logger = logging.getLogger(__name__)

async def run_api_server(host: str = "0.0.0.0", port: int = 8003):
    """
    Run the FastAPI server using uvicorn.
    This is intended to run as a background task.
    """
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    logger.info("Starting FastAPI server on %s:%d", host, port)
    await server.serve()
