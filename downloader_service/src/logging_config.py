"""
Logging configuration module for the Downloader Service.
"""

import logging
import sys
from config import settings

def setup_logging() -> logging.Logger:
    """
    Configure logging based on settings.
    """
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        stream=sys.stdout
    )
    logger = logging.getLogger("downloader_service")
    logger.debug("Logging configured at level: %s", settings.LOG_LEVEL)
    return logger

logger = setup_logging()
