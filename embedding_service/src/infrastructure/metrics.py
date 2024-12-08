"""
infrastructure/metrics.py

Sets up Prometheus metrics and starts a metrics server.
"""

import logging
from prometheus_client import Counter, Histogram, start_http_server
from infrastructure.config import settings

logger = logging.getLogger(__name__)

embeddings_generated = Counter(
    "embedding_service_embeddings_generated_total",
    "Number of embeddings successfully generated and indexed"
)
embedding_errors = Counter(
    "embedding_service_embedding_errors_total",
    "Number of embedding generation or indexing errors"
)
embedding_latency = Histogram(
    "embedding_service_embedding_latency_seconds",
    "Time taken to generate and index embeddings"
)

def start_metrics_server(port: int = 8001):
    start_http_server(port)
    logger.info("Prometheus metrics server started on port %d", port)
