"""
logging_config.py

Configures logging for the downloader service.
"""

import logging
import sys

from infrastructure.config import settings


def setup_logging() -> logging.Logger:
    """
    Configure logging based on environment settings.
    """
    logging.basicConfig(level=settings.LOG_LEVEL, format=settings.LOG_FORMAT, stream=sys.stdout)
    logger = logging.getLogger("downloader_service")
    logger.debug("Logging configured at level: %s", settings.LOG_LEVEL)
    return logger


logger = setup_logging()
