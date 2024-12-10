"""
retry.py

Provides a retry mechanism for establishing connections to external services.
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def retry_connection(connect_coro, max_retries=7, delay=10, name="service"):
    """
    Retry connecting to a service multiple times with a delay between attempts.

    Args:
        connect_coro (coroutine): Connection coroutine.
        max_retries (int): Maximum number of attempts.
        delay (int): Delay in seconds between attempts.
        name (str): Service name for logging.

    Raises:
        ConnectionError: If unable to connect after max_retries.
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info("Connecting to %s (attempt %d/%d)...", name, attempt, max_retries)
            await connect_coro()
            logger.info("Connected to %s.", name)
            return
        except Exception as e:
            logger.warning("Failed to connect to %s: %s", name, e)
            if attempt < max_retries:
                logger.info("Retrying in %d seconds...", delay)
                await asyncio.sleep(delay)
    logger.error("Could not connect to %s after %d attempts.", name, max_retries)
    raise ConnectionError(f"Failed to connect to {name}")
