"""
Configuration module for the Downloader Service.

This module defines configuration settings using Pydantic's BaseSettings
to load values from environment variables. These settings include
logging preferences, database credentials, Redis configuration,
RabbitMQ connection details, and parameters related to the download process.
"""

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """
    Settings class for the downloader service.

    Attributes:
        LOG_LEVEL (str): The log level (e.g., INFO, DEBUG).
        LOG_FORMAT (str): The log formatting string.
        PG_HOST (str): PostgreSQL host.
        PG_PORT (int): PostgreSQL port.
        PG_USER (str): PostgreSQL username.
        PG_PASSWORD (str): PostgreSQL password.
        PG_DATABASE (str): PostgreSQL database name.
        REDIS_HOST (str): Redis host.
        REDIS_PORT (int): Redis port.
        REDIS_DB (int): Redis database number.
        RABBITMQ_HOST (str): RabbitMQ host.
        RABBITMQ_PORT (int): RabbitMQ port.
        RABBITMQ_USER (str): RabbitMQ username.
        RABBITMQ_PASSWORD (str): RabbitMQ password.
        DOWNLOAD_QUEUE (str): RabbitMQ queue for image downloads.
        DOWNLOAD_TIMEOUT (int): HTTP timeout for image downloads.
        USER_AGENT (str): User-Agent string for HTTP requests.
        METRICS_PORT (int): Port for Prometheus metrics.
        IMAGE_STORAGE_PATH (str): Local path to store downloaded images.
        URLS_FILE_PATH (str): Path to the file containing URLs.
        BLOOM_EXPECTED_ITEMS (int): Expected items for Bloom filter capacity.
        BLOOM_ERROR_RATE (float): Acceptable error rate for Bloom filter.
        NUM_CONSUMERS (int): Number of consumers for RabbitMQ.
        EMBEDDING_QUEUE (str): RabbitMQ queue for embedding service.
        URL_CHUNK_SIZE (int): Number of URLs to batch-process before publishing.

    """

    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field("%(asctime)s [%(levelname)s] %(name)s: %(message)s", env="LOG_FORMAT")

    # PostgreSQL
    PG_HOST: str = Field("localhost", env="PG_HOST")
    PG_PORT: int = Field(5432, env="PG_PORT")
    PG_USER: str = Field("user", env="PG_USER")
    PG_PASSWORD: str = Field("password", env="PG_PASSWORD")
    PG_DATABASE: str = Field("mydb", env="PG_DATABASE")

    # Redis
    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")

    # RabbitMQ
    RABBITMQ_HOST: str = Field("localhost", env="RABBITMQ_HOST")
    RABBITMQ_PORT: int = Field(5672, env="RABBITMQ_PORT")
    RABBITMQ_USER: str = Field("guest", env="RABBITMQ_USER")
    RABBITMQ_PASSWORD: str = Field("guest", env="RABBITMQ_PASSWORD")
    DOWNLOAD_QUEUE: str = Field("image_downloads", env="DOWNLOAD_QUEUE")

    # Downloader
    DOWNLOAD_TIMEOUT: int = Field(30, env="DOWNLOAD_TIMEOUT")
    USER_AGENT: str = Field("MyImageDownloader/1.0", env="USER_AGENT")
    METRICS_PORT: int = Field(8000, env="METRICS_PORT")

    # File paths
    IMAGE_STORAGE_PATH: str = Field("/app/images", env="IMAGE_STORAGE_PATH")
    URLS_FILE_PATH: str = Field("/app_input/image_urls.txt", env="URLS_FILE_PATH")

    # Bloom Filter Settings
    BLOOM_EXPECTED_ITEMS: int = Field(10_000_000, env="BLOOM_EXPECTED_ITEMS")
    BLOOM_ERROR_RATE: float = Field(0.0001, env="BLOOM_ERROR_RATE")
    NUM_CONSUMERS: int = Field(4, env="NUM_CONSUMERS")

    # Embedding Queue
    EMBEDDING_QUEUE: str = Field("image_embeddings", env="EMBEDDING_QUEUE")

    # New: Chunk size for file reading
    URL_CHUNK_SIZE: int = Field(10_000, env="URL_CHUNK_SIZE")

    class Config:
        """Config for settings."""
        env_file = ".env"
        case_sensitive = True

settings = Settings()
