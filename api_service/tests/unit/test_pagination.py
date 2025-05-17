import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))
from application.pagination import paginate_results

class TestPagination(unittest.TestCase):
    def test_paginate_results(self):
        data = [{'idx': i} for i in range(10)]
        self.assertEqual(paginate_results(data, page=1, size=3), data[0:3])
        self.assertEqual(paginate_results(data, page=2, size=5), data[5:10])

if __name__ == '__main__':
    unittest.main()
