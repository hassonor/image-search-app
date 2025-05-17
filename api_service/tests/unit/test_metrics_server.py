import os
import sys
import types
import importlib
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Stub prometheus_client so metrics module can be imported without the package.
sys.modules.pop('prometheus_client', None)
prom_module = types.ModuleType('prometheus_client')

def fake_start(port):
    fake_start.called = port
fake_start.called = None

prom_module.Counter = lambda *a, **k: object()
prom_module.Histogram = lambda *a, **k: object()
prom_module.start_http_server = fake_start
sys.modules['prometheus_client'] = prom_module

import infrastructure.metrics as metrics
importlib.reload(metrics)

class TestMetricsServer(unittest.TestCase):
    def test_start_metrics_server(self):
        metrics.start_metrics_server(123)
        self.assertEqual(fake_start.called, 123)

if __name__ == '__main__':
    unittest.main()
