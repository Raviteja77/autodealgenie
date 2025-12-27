"""Tests package initialization"""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker

from app.db.session import Base, get_db
from app.main import app


# Add a compiler for JSONB on SQLite
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(element, compiler, **kw):
    """Render JSONB as JSON for SQLite."""
    return compiler.visit_json(element, **kw)


# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """Create a test client with database dependency override and mocked external services"""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    # Mock Redis connection
    mock_redis = MagicMock()
    mock_redis.connect_redis = AsyncMock()
    mock_redis.close_redis = AsyncMock()
    mock_redis.get_client = MagicMock(return_value=AsyncMock())

    # Mock RabbitMQ connection
    mock_rabbitmq = MagicMock()
    mock_rabbitmq.connect = AsyncMock()
    mock_rabbitmq.close = AsyncMock()
    mock_rabbitmq.get_channel = MagicMock(return_value=AsyncMock())

    # Mock RabbitMQ producer
    mock_rabbitmq_producer = MagicMock()
    mock_rabbitmq_producer.start = AsyncMock()
    mock_rabbitmq_producer.stop = AsyncMock()

    # Mock RabbitMQ consumer
    mock_rabbitmq_consumer = MagicMock()
    mock_rabbitmq_consumer.start = AsyncMock()
    mock_rabbitmq_consumer.stop = AsyncMock()
    mock_rabbitmq_consumer.consume_messages = MagicMock(
        return_value=AsyncMock()  # Returns a coroutine that can be used in create_task
    )

    app.dependency_overrides[get_db] = override_get_db

    with (
        patch("app.db.rabbitmq.rabbitmq", mock_rabbitmq),
        patch("app.db.redis.redis_client", mock_redis),
        patch("app.services.rabbitmq_producer.rabbitmq_producer", mock_rabbitmq_producer),
        patch("app.services.rabbitmq_consumer.deals_consumer", mock_rabbitmq_consumer),
    ):
        with TestClient(app) as test_client:
            yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def mock_current_user():
    """Mock current user for authentication-required tests"""
    from app.models.models import User

    user = User(
        id=1,
        email="testuser@example.com",
        username="testuser",
        hashed_password="$2b$12$test",  # Note: hashed_password, not password_hash
        is_active=True,
    )
    return user
