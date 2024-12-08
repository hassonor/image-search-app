"""
application/models.py

Data models for the API responses.
"""

from pydantic import BaseModel

class SearchResult(BaseModel):
    image_id: int
    image_url: str
    score: float
