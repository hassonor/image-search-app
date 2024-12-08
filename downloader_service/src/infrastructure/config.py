"""
config.py

Provides configuration settings for the downloader service using pydantic's BaseSettings.
Loads values from environment variables.
"""

from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Logging
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
    EMBEDDING_QUEUE: str = Field("image_embeddings", env="EMBEDDING_QUEUE")

    # Downloader
    DOWNLOAD_TIMEOUT: int = Field(30, env="DOWNLOAD_TIMEOUT")
    USER_AGENT: str = Field("MyImageDownloader/1.0", env="USER_AGENT")
    METRICS_PORT: int = Field(8000, env="METRICS_PORT")

    # File paths
    IMAGE_STORAGE_PATH: str = Field("/app/images", env="IMAGE_STORAGE_PATH")
    URLS_FILE_PATH: str = Field("/app_input/image_urls.txt", env="URLS_FILE_PATH")

    # Bloom Filter
    BLOOM_EXPECTED_ITEMS: int = Field(10_000_000, env="BLOOM_EXPECTED_ITEMS")
    BLOOM_ERROR_RATE: float = Field(0.0001, env="BLOOM_ERROR_RATE")

    # Number of Consumers
    NUM_CONSUMERS: int = Field(4, env="NUM_CONSUMERS")

    # Chunk size for file reading
    URL_CHUNK_SIZE: int = Field(10_000, env="URL_CHUNK_SIZE")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
