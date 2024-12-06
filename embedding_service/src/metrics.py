from prometheus_client import Counter, Histogram, start_http_server
import logging

logger = logging.getLogger(__name__)

# Prometheus metrics
embeddings_generated = Counter('embedding_service_embeddings_generated_total', 'Number of embeddings successfully generated and indexed')
embedding_errors = Counter('embedding_service_embedding_errors_total', 'Number of embedding generation errors')
embedding_latency = Histogram('embedding_service_embedding_latency_seconds', 'Time taken to generate and index embeddings')


def start_metrics_server(port: int = 8001):
    """
    Start Prometheus metrics server on the given port.

    Args:
        port (int): Port number to start the metrics server on.
    """
    try:
        start_http_server(port)
        logger.info("Prometheus metrics server started on port %d", port)
    except Exception as e:
        logger.exception("Failed to start Prometheus metrics server: %s", e)
        raise
