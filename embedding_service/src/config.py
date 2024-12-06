from pydantic import BaseSettings, Field


class Settings(BaseSettings):
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
