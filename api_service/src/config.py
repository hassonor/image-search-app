from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # Logging
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field("%(asctime)s [%(levelname)s] %(name)s: %(message)s", env="LOG_FORMAT")

    # Elasticsearch Settings
    ELASTICSEARCH_HOST: str = Field("elasticsearch", env="ELASTICSEARCH_HOST")
    ELASTICSEARCH_PORT: int = Field(9200, env="ELASTICSEARCH_PORT")
    ELASTICSEARCH_INDEX: str = Field("image_embeddings", env="ELASTICSEARCH_INDEX")
    TOP_K_VALUE: int = Field(50, env="TOP_K_VALUE")
    # Embedding Model Settings
    EMBEDDING_MODEL: str = Field("ViT-B/32", env="EMBEDDING_MODEL")

    # Metrics
    METRICS_PORT: int = Field(8002, env="METRICS_PORT")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
