"""
application/pagination.py

Pagination utility functions for slicing query results.
"""

from typing import List

def paginate_results(results: List[dict], page: int, size: int) -> List[dict]:
    """
    Paginate a list of results.

    Args:
        results (List[dict]): Full list of results from Elasticsearch.
        page (int): Current page number.
        size (int): Items per page.

    Returns:
        List[dict]: Slice of results for the requested page.
    """
    start_index = (page - 1) * size
    end_index = start_index + size
    return results[start_index:end_index]
