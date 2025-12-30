"""Service-wide configuration constants"""


class ServiceConfig:
    """Configuration for all services"""

    # Logging
    LOG_AI_RESPONSES = True
    LOG_EXCEPTIONS = True
    LOG_PERFORMANCE = True

    # Retry settings
    MAX_RETRIES = 3
    RETRY_BACKOFF_FACTOR = 2

    # LLM settings
    DEFAULT_LLM_TEMPERATURE = 0.7
    DEFAULT_LLM_MAX_TOKENS = 1000

    # Database
    DB_POOL_SIZE = 20
    DB_MAX_OVERFLOW = 0

    # Cache settings
    CACHE_TTL_SECONDS = 3600  # 1 hour

    # API rate limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW_SECONDS = 60


class MarketDataConfig:
    """Configuration for market intelligence services"""

    MAX_COMPARABLES = 10
    SEARCH_RADIUS_MILES = 50
    CACHE_MARKET_DATA_HOURS = 24
    PRICE_TREND_LOOKBACK_DAYS = 90


class DealEvaluationConfig:
    """Configuration for deal evaluation"""

    FAIR_VALUE_WEIGHT = 0.4
    MARKET_DATA_WEIGHT = 0.3
    VEHICLE_CONDITION_WEIGHT = 0.3

    # Score thresholds
    EXCELLENT_SCORE = 8.0
    GOOD_SCORE = 6.0
    FAIR_SCORE = 4.0
