from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    In Pydantic v2, field names automatically map to environment variables.
    For example, LOG_LEVEL field will read from LOG_LEVEL env var.
    The default values are used if the environment variable is not set.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    # PostgreSQL
    PG_HOST: str = Field(default="localhost")
    PG_PORT: int = Field(default=5432)
    PG_USER: str = Field(default="user")
    PG_PASSWORD: str = Field(default="password")
    PG_DATABASE: str = Field(default="mydb")

    # Redis
    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)

    # RabbitMQ
    RABBITMQ_HOST: str = Field(default="localhost")
    RABBITMQ_PORT: int = Field(default=5672)
    RABBITMQ_USER: str = Field(default="guest")
    RABBITMQ_PASSWORD: str = Field(default="guest")
    DOWNLOAD_QUEUE: str = Field(default="image_downloads")
    EMBEDDING_QUEUE: str = Field(default="image_embeddings")

    # Downloader
    DOWNLOAD_TIMEOUT: int = Field(default=30)
    USER_AGENT: str = Field(default="MyImageDownloader/1.0")
    METRICS_PORT: int = Field(default=8000)

    IMAGE_STORAGE_PATH: str = Field(default="/app/images")

    BLOOM_EXPECTED_ITEMS: int = Field(default=10_000_000)
    BLOOM_ERROR_RATE: float = Field(default=0.0001)

    NUM_CONSUMERS: int = Field(default=4)

settings = Settings()
