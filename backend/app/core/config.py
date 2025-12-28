"""
Core configuration settings for AutoDealGenie
"""

from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    # Project Info
    PROJECT_NAME: str = "AutoDealGenie API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "AI-powered automotive deal management platform"
    API_V1_STR: str = "/api/v1"

    LOG_LEVEL: str = "INFO"  # "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"

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

    # Redis (optional for GCP Free Tier - will use in-memory cache if not available)
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    USE_REDIS: bool = True  # Set to False to use in-memory caching

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # RabbitMQ (optional for GCP Free Tier - will use in-memory queue if not available)
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "autodealgenie"
    RABBITMQ_PASSWORD: str = "autodealgenie_password"
    RABBITMQ_VHOST: str = "/"
    RABBITMQ_QUEUE_DEALS: str = "deals"
    RABBITMQ_QUEUE_NOTIFICATIONS: str = "notifications"
    USE_RABBITMQ: bool = True  # Set to False to use in-memory queue

    @property
    def RABBITMQ_URL(self) -> str:
        # Encode username and password to handle special characters
        encoded_user = quote_plus(self.RABBITMQ_USER)
        encoded_password = quote_plus(self.RABBITMQ_PASSWORD)
        return f"amqp://{encoded_user}:{encoded_password}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}{self.RABBITMQ_VHOST}"

    # OpenAI / OpenRouter
    OPENAI_API_KEY: str | None = None
    OPENROUTER_API_KEY: str | None = None  # OpenRouter API key (preferred if set)
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_BASE_URL: str | None = None  # Optional: Use for OpenRouter or custom endpoints

    # MarketCheck API
    MARKET_CHECK_API_KEY: str | None = None
    MAX_SEARCH_RESULTS: int = 50  # Maximum number of results to fetch from API for LLM analysis

    # Security
    SECRET_KEY: str  # REQUIRED: Must be set via environment variable (min 32 chars)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 1
    PASSWORD_RESET_TOKEN_LENGTH: int = 32

    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production

    # Mock Services (for development/testing)
    USE_MOCK_SERVICES: bool = False

    def __init__(self, **kwargs):
        """Initialize settings and validate critical security configurations"""
        super().__init__(**kwargs)
        self._validate_security_settings()

    def _validate_security_settings(self):
        """Validate critical security settings at startup"""
        # Validate SECRET_KEY
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable is required")
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")

        # Warn about development-only configurations in production
        if self.ENVIRONMENT == "production":
            if (
                self.SECRET_KEY
                == "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
            ):
                raise ValueError("Default SECRET_KEY detected in production environment")
            if not self.POSTGRES_PASSWORD:
                raise ValueError("POSTGRES_PASSWORD must be set in production")
            if "localhost" in str(self.BACKEND_CORS_ORIGINS):
                raise ValueError("Localhost CORS origins not allowed in production")

    @property
    def COOKIE_SECURE(self) -> bool:
        """Use secure cookies in production only"""
        return self.ENVIRONMENT == "production"

    @property
    def ACCESS_TOKEN_EXPIRE_SECONDS(self) -> int:
        """Access token expiry in seconds for cookie max_age"""
        return self.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    @property
    def REFRESH_TOKEN_EXPIRE_SECONDS(self) -> int:
        """Refresh token expiry in seconds for cookie max_age"""
        return self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="allow")


settings = Settings()
