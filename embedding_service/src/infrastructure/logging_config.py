"""
logging_config.py

Configures logging for the embedding service.
"""

import logging
import sys
from infrastructure.config import settings


def setup_logging():
    """
    Configure logging based on settings from config.
    Uses stdout for log output.
    """
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        stream=sys.stdout,
    )
    logger = logging.getLogger("embedding_service")
    logger.debug("Logging configured at level: %s", settings.LOG_LEVEL)
    return logger


logger = setup_logging()
