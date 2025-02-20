"""
infrastructure/metrics.py

Defines Prometheus metrics and starts a metrics server for the API service.
"""

from prometheus_client import Counter, Histogram, start_http_server
import logging

logger = logging.getLogger(__name__)

queries_total = Counter(
    "ui_service_queries_total",
    "Total number of search queries received",
)
query_errors_total = Counter(
    "ui_service_query_errors_total",
    "Total number of search query errors",
)
query_latency = Histogram(
    "ui_service_query_latency_seconds",
    "Time taken to process search queries",
)

def start_metrics_server(port: int = 8002) -> None:
    """
    Start Prometheus metrics server on the given port.

    Args:
        port (int): Port number for metrics server.
    """
    try:
        start_http_server(port)
        logger.info("Prometheus metrics server started on port %d", port)
    except Exception as e:
        logger.exception("Failed to start Prometheus metrics server: %s", e)
        raise
