"""
infrastructure/config.py

Provides configuration settings for the API service using pydantic BaseSettings.
Loads values from environment variables.

In Pydantic v2, field names automatically map to environment variables.
For example, LOG_LEVEL field will read from LOG_LEVEL env var.
The default values are used if the environment variable is not set.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # Elasticsearch Settings
    ELASTICSEARCH_HOST: str = Field(default="elasticsearch")
    ELASTICSEARCH_PORT: int = Field(default=9200)
    ELASTICSEARCH_INDEX: str = Field(default="image_embeddings")
    TOP_K_VALUE: int = Field(default=50)

    # Embedding Model Settings
    EMBEDDING_MODEL: str = Field(default="ViT-B/32")

    # Metrics
    METRICS_PORT: int = Field(default=8002)

settings = Settings()
