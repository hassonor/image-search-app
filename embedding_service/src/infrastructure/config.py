"""
config.py

Provides configuration settings for the embedding service using pydantic BaseSettings.
Values are loaded from environment variables defined in a .env file.
"""

from pydantic import BaseSettings, Field

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

    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field("%(asctime)s [%(levelname)s] %(name)s: %(message)s", env="LOG_FORMAT")

    # RabbitMQ Settings
    RABBITMQ_HOST: str = Field("rabbitmq", env="RABBITMQ_HOST")
    RABBITMQ_PORT: int = Field(5672, env="RABBITMQ_PORT")
    RABBITMQ_USER: str = Field("guest", env="RABBITMQ_USER")
    RABBITMQ_PASSWORD: str = Field("guest", env="RABBITMQ_PASSWORD")

    # Number of Consumers
    NUM_CONSUMERS: int = Field(10, env="NUM_CONSUMERS")

    # Elasticsearch Settings
    ELASTICSEARCH_HOST: str = Field("elasticsearch", env="ELASTICSEARCH_HOST")
    ELASTICSEARCH_PORT: int = Field(9200, env="ELASTICSEARCH_PORT")
    ELASTICSEARCH_INDEX: str = Field("image_embeddings", env="ELASTICSEARCH_INDEX")

    # Embedding Model Settings
    EMBEDDING_MODEL: str = Field("ViT-B/32", env="EMBEDDING_MODEL")

    # Metrics
    METRICS_PORT: int = Field(8001, env="METRICS_PORT")

    # Embedding Queue
    EMBEDDING_QUEUE: str = Field("image_embeddings", env="EMBEDDING_QUEUE")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
