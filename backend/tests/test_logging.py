import json
import logging
import sys
from unittest.mock import patch

import pytest

from app.core.logging import JSONFormatter, configure_logging


# Fixture to reset logging after each test
@pytest.fixture(autouse=True)
def reset_logging():
    # Setup: save original handlers and level
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level

    yield

    # Teardown: restore original handlers and level
    root.handlers = original_handlers
    root.setLevel(original_level)


def test_configure_logging_handlers():
    """Test that configure_logging sets up handlers correctly."""
    with patch("app.core.logging.settings") as mock_settings:
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.ENVIRONMENT = "development"

        configure_logging()

        root = logging.getLogger()
        assert len(root.handlers) == 1
        assert isinstance(root.handlers[0], logging.StreamHandler)
        assert root.handlers[0].stream == sys.stdout


def test_json_formatter_production_mode():
    """Test that JSON formatter is used in production mode."""
    with patch("app.core.logging.settings") as mock_settings:
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.ENVIRONMENT = "production"

        configure_logging()

        root = logging.getLogger()
        handler = root.handlers[0]
        assert isinstance(handler.formatter, JSONFormatter)

        # Verify it produces valid JSON
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        formatted = handler.formatter.format(record)
        data = json.loads(formatted)
        assert data["message"] == "test message"
        assert data["level"] == "INFO"


def test_standard_formatter_development_mode():
    """Test that standard formatter is used in development mode."""
    with patch("app.core.logging.settings") as mock_settings:
        mock_settings.LOG_LEVEL = "INFO"
        mock_settings.ENVIRONMENT = "development"

        configure_logging()

        root = logging.getLogger()
        handler = root.handlers[0]
        assert not isinstance(handler.formatter, JSONFormatter)
        assert isinstance(handler.formatter, logging.Formatter)

        # Verify format string output
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname=__file__,
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None,
        )
        formatted = handler.formatter.format(record)
        assert "test_logger" in formatted
        assert "INFO" in formatted
        assert "test message" in formatted


def test_log_level_applied():
    """Test that log level is correctly applied from settings."""
    with patch("app.core.logging.settings") as mock_settings:
        mock_settings.LOG_LEVEL = "DEBUG"
        mock_settings.ENVIRONMENT = "development"

        configure_logging()

        root = logging.getLogger()
        assert root.level == logging.DEBUG


def test_request_id_inclusion():
    """Test that request_id is included in logs when present."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="test message",
        args=(),
        exc_info=None,
    )

    # Case 1: No request_id
    formatted = formatter.format(record)
    data = json.loads(formatted)
    assert "request_id" not in data

    # Case 2: With request_id
    record.request_id = "req-123"
    formatted = formatter.format(record)
    data = json.loads(formatted)
    assert data["request_id"] == "req-123"
