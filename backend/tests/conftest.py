"""Tests package initialization"""

from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_async_db, get_db
from app.main import app


# Add a compiler for JSONB on SQLite - render as TEXT
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    """Render JSONB as TEXT for SQLite compatibility."""
    return "TEXT"


# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
SQLALCHEMY_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Sync engine for legacy tests
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async engine for async tests
async_engine = create_async_engine(
    SQLALCHEMY_ASYNC_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)
AsyncTestingSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False, autocommit=False, autoflush=False
)


@pytest.fixture(scope="function")
def db() -> Generator:
    """Create a fresh database for each test (sync)"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest_asyncio.fixture(scope="function")
async def async_db() -> AsyncGenerator:
    """Create a fresh async database for each test"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncTestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(async_db) -> Generator:
    """Create a test client with database dependency override and mocked external services"""

    async def override_get_async_db():
        try:
            yield async_db
        finally:
            pass

    def override_get_db():
        # Provide sync db for any legacy code that still uses it
        sync_db = TestingSessionLocal()
        try:
            yield sync_db
        finally:
            sync_db.close()

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
    app.dependency_overrides[get_async_db] = override_get_async_db

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
