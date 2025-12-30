"""Standardized error classes for the application"""
from app.utils.error_handler import ApiError


class NegotiationError(ApiError):
    """Errors related to negotiation operations"""

    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(status_code=status_code, message=message, details=details)


class MarketDataError(ApiError):
    """Errors related to market data retrieval"""

    def __init__(self, message: str, status_code: int = 503, details: dict | None = None):
        super().__init__(status_code=status_code, message=message, details=details)


class LLMServiceError(ApiError):
    """Errors related to LLM service calls"""

    def __init__(self, message: str, status_code: int = 503, details: dict | None = None):
        super().__init__(status_code=status_code, message=message, details=details)


class DealEvaluationError(ApiError):
    """Errors related to deal evaluation"""

    def __init__(self, message: str, status_code: int = 400, details: dict | None = None):
        super().__init__(status_code=status_code, message=message, details=details)


class ValidationError(ApiError):
    """Errors related to input validation"""

    def __init__(self, message: str, status_code: int = 422, details: dict | None = None):
        super().__init__(status_code=status_code, message=message, details=details)
