"""
application/retry.py

Provides a retry mechanism for establishing connections to external services.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)

async def retry_connection(connect_coro, max_retries=7, delay=10, name="service"):
    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Trying to connect to %s (attempt %d/%d)...", name, attempt, max_retries)
            await connect_coro()
            logger.info("Successfully connected to %s.", name)
            return
        except Exception as e:
            logger.warning("Failed to connect to %s (attempt %d/%d): %s", name, attempt, max_retries, e)
            if attempt < max_retries:
                logger.info("Waiting %d seconds before retrying...", delay)
                await asyncio.sleep(delay)
    logger.error("Could not connect to %s after %d attempts.", name, max_retries)
    raise ConnectionError(f"Failed to connect to {name}")
