from prometheus_client import Counter, Histogram, start_http_server
import logging
from config import settings

logger = logging.getLogger(__name__)

# Prometheus metrics
images_downloaded = Counter('downloader_images_downloaded_total', 'Number of images successfully downloaded')
download_errors = Counter('downloader_download_errors_total', 'Number of download errors')
download_latency = Histogram('downloader_download_latency_seconds', 'Time taken to download images')


def start_metrics_server(port: int = 8000):
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
