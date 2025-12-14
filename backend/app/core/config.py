"""
Core configuration settings for AutoDealGenie
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Project Info
    PROJECT_NAME: str = "AutoDealGenie API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered automotive deal management platform"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # PostgreSQL
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "autodealgenie"
    POSTGRES_PASSWORD: str = ""  # REQUIRED: Must be set via environment variable
    POSTGRES_DB: str = "autodealgenie"
    POSTGRES_PORT: int = 5432

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "autodealgenie"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_CONSUMER_GROUP: str = "autodealgenie-consumer"
    KAFKA_TOPIC_DEALS: str = "deals"
    KAFKA_TOPIC_NOTIFICATIONS: str = "notifications"

    # OpenAI
    OPENAI_API_KEY: str | None = None
    OPENAI_MODEL: str = "gpt-4"

    # MarketCheck API
    MARKET_CHECK_API_KEY: str | None = None

    # Security
    SECRET_KEY: str = ""  # REQUIRED: Must be set via environment variable (min 32 chars)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    
    @property
    def COOKIE_SECURE(self) -> bool:
        """Use secure cookies in production only"""
        return self.ENVIRONMENT == "production"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="allow")


settings = Settings()
