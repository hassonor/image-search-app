"""
shutdown.py

Handles graceful shutdown signals for the asyncio event loop.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


def shutdown():
    """Handle shutdown signals by canceling all running asyncio tasks."""
    logger.info("Shutdown signal received. Stopping service...")
    for task in asyncio.all_tasks():
        task.cancel()

