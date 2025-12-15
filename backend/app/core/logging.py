import logging
import sys
import json
from typing import Any
from app.core.config import settings

class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging in production.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        
        # Add request ID if available
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id  # type: ignore
            
        # Add exception info if available
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_obj)

def configure_logging() -> None:
    """
    Configure logging based on environment settings.
    """
    root_logger = logging.getLogger()
    
    # Determine log level (default to INFO if not set in settings)
    log_level = getattr(settings, "LOG_LEVEL", "INFO").upper()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    root_logger.handlers = []
    
    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # Determine environment (default to development if not set)
    env = getattr(settings, "ENVIRONMENT", "development").lower()
    
    if env == "production":
        # Use JSON formatter for production
        handler.setFormatter(JSONFormatter())
    else:
        # Use standard readable formatter for development
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)
        
    root_logger.addHandler(handler)
