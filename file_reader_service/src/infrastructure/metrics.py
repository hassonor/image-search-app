import logging
from prometheus_client import start_http_server

logger = logging.getLogger(__name__)

def start_metrics_server(port: int = 8005) -> None:
    try:
        start_http_server(port)
        logger.info("Prometheus metrics server started on port %d", port)
    except Exception as e:
        logger.exception("Failed to start metrics server: %s", e)
        raise
