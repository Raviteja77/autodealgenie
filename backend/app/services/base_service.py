import logging
from collections.abc import Callable
from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.utils.error_handler import ApiError

T = TypeVar("T")
logger = logging.getLogger(__name__)


class BaseService:
    """Base class for all services providing common DB and error patterns."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute_with_retry(
        self, func: Callable[..., T], max_retries: int = 3, *args, **kwargs
    ) -> T:
        """Common retry wrapper for I/O bound tasks."""
        last_exception = None
        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")

        raise ApiError(
            status_code=500,
            message="Operation failed after multiple retries",
            details={"error": str(last_exception)},
        )

    def log_operation(self, operation: str, data: dict[str, Any]):
        """Structured logging for service operations."""
        logger.info(f"Service Operation: {operation} | Context: {data}")
