"""Base service class with common patterns for all services"""
import logging
from typing import Any, Callable
from sqlalchemy.ext.asyncio import AsyncSession


logger = logging.getLogger(__name__)


class BaseService:
    """
    Base class for all services with common patterns.

    Provides:
    - Database session management
    - Common error handling
    - Logging patterns
    - Retry logic
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize base service.

        Args:
            db: Async database session
        """
        self.db = db
        self.logger = logging.getLogger(self.__class__.__name__)

    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        max_retries: int = 3,
        **kwargs
    ) -> Any:
        """
        Execute a function with retry logic.

        Args:
            func: Function to execute
            args: Positional arguments for the function
            max_retries: Maximum number of retry attempts
            kwargs: Keyword arguments for the function

        Returns:
            Result from the function

        Raises:
            Exception: If all retries fail
        """
        last_exception = None

        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                self.logger.warning(
                    f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}"
                )
                if attempt == max_retries - 1:
                    self.logger.error(f"All {max_retries} attempts failed")
                    raise last_exception

        raise last_exception

    async def log_operation(
        self,
        operation: str,
        data: dict[str, Any],
        level: str = "info"
    ):
        """
        Log an operation with structured data.

        Args:
            operation: Name of the operation
            data: Data to log
            level: Logging level (info, warning, error)
        """
        log_func = getattr(self.logger, level, self.logger.info)
        log_func(f"{operation}: {data}")

    async def rollback_on_error(self):
        """Rollback database transaction on error"""
        try:
            await self.db.rollback()
            self.logger.info("Database transaction rolled back")
        except Exception as e:
            self.logger.error(f"Error during rollback: {str(e)}")
