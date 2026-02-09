"""
config.py

Provides configuration settings for the embedding service using pydantic BaseSettings.
Values are loaded from environment variables defined in a .env file.

In Pydantic v2, field names automatically map to environment variables.
For example, LOG_LEVEL field will read from LOG_LEVEL env var.
The default values are used if the environment variable is not set.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuration settings for the embedding service.
    Loads values from environment variables and falls back to defaults if not set.

    Attributes:
        LOG_LEVEL (str): The log level (e.g., "INFO", "DEBUG").
        LOG_FORMAT (str): The format for log messages.
        RABBITMQ_HOST (str): The RabbitMQ host address.
        RABBITMQ_PORT (int): The RabbitMQ port number.
        RABBITMQ_USER (str): The RabbitMQ username.
        RABBITMQ_PASSWORD (str): The RabbitMQ password.
        NUM_CONSUMERS (int): Number of consumers for the RabbitMQ queue.
        ELASTICSEARCH_HOST (str): The Elasticsearch host address.
        ELASTICSEARCH_PORT (int): The Elasticsearch port number.
        ELASTICSEARCH_INDEX (str): The Elasticsearch index name for embeddings.
        EMBEDDING_MODEL (str): The model name used for embedding generation.
        METRICS_PORT (int): Port where Prometheus metrics are served.
        EMBEDDING_QUEUE (str): The RabbitMQ queue for embeddings.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # RabbitMQ Settings
    RABBITMQ_HOST: str = Field(default="rabbitmq")
    RABBITMQ_PORT: int = Field(default=5672)
    RABBITMQ_USER: str = Field(default="guest")
    RABBITMQ_PASSWORD: str = Field(default="guest")

    # Number of Consumers
    NUM_CONSUMERS: int = Field(default=10)

    # Elasticsearch Settings
    ELASTICSEARCH_HOST: str = Field(default="elasticsearch")
    ELASTICSEARCH_PORT: int = Field(default=9200)
    ELASTICSEARCH_INDEX: str = Field(default="image_embeddings")

    # Embedding Model Settings
    EMBEDDING_MODEL: str = Field(default="ViT-B/32")

    # Metrics
    METRICS_PORT: int = Field(default=8001)

    # Embedding Queue
    EMBEDDING_QUEUE: str = Field(default="image_embeddings")


settings = Settings()
