"""
application/models.py

Data models for the API responses.
"""

from pydantic import BaseModel
from typing import List

class SearchResult(BaseModel):
    image_id: int
    image_url: str
    score: float

class FullSearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
