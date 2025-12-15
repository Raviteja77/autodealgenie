"""
Error handling middleware for standardized API error responses.

This middleware intercepts ApiError exceptions and returns structured
JSON responses with consistent formatting. It also logs errors for debugging.
"""

import logging
from collections.abc import Callable

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.error_handler import ApiError

# Configure logger for error middleware
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle ApiError exceptions and return structured JSON responses.

    This middleware catches ApiError exceptions thrown anywhere in the application
    and converts them to standardized JSON error responses. It also logs the errors
    for debugging and monitoring purposes.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process the request and handle any ApiError exceptions.

        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler in the chain

        Returns:
            JSONResponse: Error response if ApiError is raised, otherwise normal response
        """
        try:
            # Process the request
            response = await call_next(request)
            return response
        except ApiError as error:
            # Log the API error
            logger.error(
                f"API Error: {error.status_code} - {error.message}",
                extra={
                    "error_status_code": error.status_code,
                    "error_message": error.message,
                    "error_details": error.details,
                    "request_path": request.url.path,
                    "request_method": request.method,
                },
            )

            # Return structured JSON error response
            return JSONResponse(
                status_code=error.status_code,
                content={
                    "detail": error.message,
                    "status_code": error.status_code,
                    **({"details": error.details} if error.details else {}),
                },
            )
        except Exception:
            # Log unexpected errors
            logger.exception(
                f"Unexpected error in {request.method} {request.url.path}",
                extra={
                    "request_path": request.url.path,
                    "request_method": request.method,
                },
            )

            # Return generic 500 error for unexpected exceptions
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "Internal server error",
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                },
            )


# Convenience function to add middleware to app
def error_middleware(app):
    """
    Add error handling middleware to the FastAPI application.

    Args:
        app: FastAPI application instance
    """
    app.add_middleware(ErrorHandlerMiddleware)
