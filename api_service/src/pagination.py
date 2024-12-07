"""
Pagination utility functions for the API Service.
"""

from typing import List


def paginate_results(results: List[dict], page: int, size: int) -> List[dict]:
    """
    Paginate a list of results.

    Args:
        results (List[dict]): The full list of results from Elasticsearch.
        page (int): The current page number.
        size (int): The number of items per page.

    Returns:
        List[dict]: The slice of results corresponding to the requested page.
    """
    start_index = (page - 1) * size
    end_index = start_index + size
    return results[start_index:end_index]