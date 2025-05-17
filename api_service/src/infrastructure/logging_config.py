"""
infrastructure/logging_config.py

Configures logging for the API service based on the settings.
"""

import logging
import sys
from infrastructure.config import settings

def setup_logging() -> logging.Logger:
    """
    Configure logging with the specified log level and format.
    """
    logging.basicConfig(
        level=settings.LOG_LEVEL,
        format=settings.LOG_FORMAT,
        stream=sys.stdout
    )
    logger = logging.getLogger("ui_service")
    logger.debug("Logging configured at level: %s", settings.LOG_LEVEL)
    return logger

logger = setup_logging()
