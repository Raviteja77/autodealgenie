"""
Custom exception classes for structured error handling in the API.

This module provides a custom ApiError exception class that allows for
structured error responses with status codes, messages, and additional details.
"""

from typing import Any


class ApiError(Exception):
    """
    Custom exception class for API errors.

    This exception class allows creation of structured error objects with
    status_code, message, and optional additional details.

    Attributes:
        status_code: HTTP status code for the error (e.g., 400, 404, 500)
        message: Human-readable error message
        details: Optional additional error details (e.g., validation errors)
    """

    def __init__(
        self,
        status_code: int,
        message: str,
        details: Any | None = None,
    ):
        """
        Initialize ApiError with status code, message, and optional details.

        Args:
            status_code: HTTP status code
            message: Error message
            details: Optional additional error information
        """
        self.status_code = status_code
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """String representation of the error."""
        if self.details:
            return f"ApiError({self.status_code}): {self.message} - {self.details}"
        return f"ApiError({self.status_code}): {self.message}"

    def __repr__(self) -> str:
        """Developer-friendly representation of the error."""
        return (
            f"ApiError(status_code={self.status_code}, "
            f"message={self.message!r}, details={self.details!r})"
        )

    def to_dict(self) -> dict:
        """
        Convert error to dictionary format for JSON responses.

        Returns:
            Dictionary with status_code, message, and optional details
        """
        error_dict = {
            "status_code": self.status_code,
            "message": self.message,
        }
        if self.details is not None:
            error_dict["details"] = self.details
        return error_dict


class NegotiationError(ApiError):
    """Errors specifically occurring during the negotiation flow."""

    def __init__(self, message: str, details: Any | None = None):
        super().__init__(status_code=400, message=message, details=details)


class MarketDataError(ApiError):
    """Errors when fetching or processing market intelligence."""

    def __init__(self, message: str, details: Any | None = None):
        super().__init__(status_code=502, message=message, details=details)
