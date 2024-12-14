from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field("%(asctime)s [%(levelname)s] %(name)s: %(message)s", env="LOG_FORMAT")

    RABBITMQ_HOST: str = Field("localhost", env="RABBITMQ_HOST")
    RABBITMQ_PORT: int = Field(5672, env="RABBITMQ_PORT")
    RABBITMQ_USER: str = Field("guest", env="RABBITMQ_USER")
    RABBITMQ_PASSWORD: str = Field("guest", env="RABBITMQ_PASSWORD")
    DOWNLOAD_QUEUE: str = Field("image_downloads", env="DOWNLOAD_QUEUE")

    REDIS_HOST: str = Field("localhost", env="REDIS_HOST")
    REDIS_PORT: int = Field(6379, env="REDIS_PORT")
    REDIS_DB: int = Field(0, env="REDIS_DB")

    URLS_FILE_PATH: str = Field("/app_input/image_urls.txt", env="URLS_FILE_PATH")
    URL_CHUNK_SIZE: int = Field(10000, env="URL_CHUNK_SIZE")

    # Bloom Filter
    BLOOM_EXPECTED_ITEMS: int = Field(10_000_000, env="BLOOM_EXPECTED_ITEMS")
    BLOOM_ERROR_RATE: float = Field(0.0001, env="BLOOM_ERROR_RATE")

    METRICS_PORT: int = Field(8005, env="METRICS_PORT")
    API_PORT: int = Field(8006, env="API_PORT")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
