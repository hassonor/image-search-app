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

    RABBITMQ_HOST: str = Field(default="localhost")
    RABBITMQ_PORT: int = Field(default=5672)
    RABBITMQ_USER: str = Field(default="guest")
    RABBITMQ_PASSWORD: str = Field(default="guest")
    DOWNLOAD_QUEUE: str = Field(default="image_downloads")

    REDIS_HOST: str = Field(default="localhost")
    REDIS_PORT: int = Field(default=6379)
    REDIS_DB: int = Field(default=0)

    URLS_FILE_PATH: str = Field(default="/app_input/image_urls.txt")
    URL_CHUNK_SIZE: int = Field(default=10000)

    # Bloom Filter
    BLOOM_EXPECTED_ITEMS: int = Field(default=10_000_000)
    BLOOM_ERROR_RATE: float = Field(default=0.0001)

    METRICS_PORT: int = Field(default=8005)
    API_PORT: int = Field(default=8006)

settings = Settings()
