import logging
import sys
from config import settings


def setup_logging():
    """
    Configure logging based on settings.
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
