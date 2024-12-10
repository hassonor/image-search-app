"""
metrics.py

Sets up Prometheus metrics for the downloader service.
Defines counters and histograms, and provides a method to start the metrics server.
"""

import logging

from prometheus_client import Counter, Histogram, start_http_server

logger = logging.getLogger(__name__)

images_downloaded = Counter(
    "downloader_images_downloaded_total", "Number of images successfully downloaded"
)
download_errors = Counter(
    "downloader_download_errors_total", "Number of download errors encountered"
)
download_latency = Histogram(
    "downloader_download_latency_seconds", "Time taken to download images"
)


def start_metrics_server(port: int = 8000) -> None:
    """
    Start Prometheus metrics server on the given port.

    Args:
        port (int): Port to run the metrics server.
    """
    try:
        start_http_server(port)
        logger.info("Prometheus metrics server started on port %d", port)
    except Exception as e:
        logger.exception("Failed to start Prometheus metrics server: %s", e)
        raise
