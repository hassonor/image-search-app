import os
import sys
import types
import unittest
from unittest.mock import patch

root_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, root_path)


class TestStartMetricsServer(unittest.TestCase):
    def test_start_metrics_server(self):
        with patch("infrastructure.metrics.start_http_server") as mock_http, patch(
            "infrastructure.metrics.logger"
        ) as mock_logger:
            from infrastructure import metrics

            metrics.start_metrics_server(1234)
            mock_http.assert_called_once_with(1234)
            mock_logger.info.assert_called_once()
