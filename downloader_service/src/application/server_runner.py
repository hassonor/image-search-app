"""
server_runner.py

Runs the FastAPI server for the downloader service in a background task.
"""

import logging

import uvicorn

from interface.api import app

logger = logging.getLogger(__name__)


async def run_api_server(host: str = "0.0.0.0", port: int = 8003):
    """
    Run the FastAPI API server as a background task.

    Args:
        host (str): Host address to bind.
        port (int): Port number for the server.
    """
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    logger.info("Starting FastAPI server on %s:%d", host, port)
    await server.serve()
