import os
import sys
import types
import importlib
import unittest
from unittest.mock import MagicMock

root_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
sys.path.insert(0, os.path.abspath(root_path))


class TestMetrics(unittest.TestCase):
    def tearDown(self):
        sys.modules.pop('prometheus_client', None)
        sys.modules.pop('infrastructure.metrics', None)

    def test_start_metrics_server_success(self):
        prom_module = types.ModuleType('prometheus_client')
        prom_module.start_http_server = MagicMock()
        prom_module.Counter = MagicMock
        prom_module.Histogram = MagicMock
        sys.modules['prometheus_client'] = prom_module

        import infrastructure.metrics as metrics
        importlib.reload(metrics)
        metrics.start_metrics_server(port=1234)
        prom_module.start_http_server.assert_called_once_with(1234)

    def test_start_metrics_server_failure(self):
        prom_module = types.ModuleType('prometheus_client')
        prom_module.start_http_server = MagicMock(side_effect=Exception('boom'))
        prom_module.Counter = MagicMock
        prom_module.Histogram = MagicMock
        sys.modules['prometheus_client'] = prom_module

        import infrastructure.metrics as metrics
        importlib.reload(metrics)
        with self.assertRaises(Exception):
            metrics.start_metrics_server(port=1234)


if __name__ == '__main__':
    unittest.main()
