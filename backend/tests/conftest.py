"""Tests package initialization"""

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.session import Base, get_db
from app.main import app

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

    # Mock MongoDB connection
    mock_mongodb = MagicMock()
    mock_mongodb.connect_db = AsyncMock()
    mock_mongodb.close_db = AsyncMock()
    mock_mongodb.get_database = MagicMock()
    mock_mongodb.get_collection = MagicMock()

    # Mock Redis connection
    mock_redis = MagicMock()
    mock_redis.connect_redis = AsyncMock()
    mock_redis.close_redis = AsyncMock()
    mock_redis.get_client = MagicMock(return_value=AsyncMock())

    # Mock Kafka producer
    mock_kafka_producer = MagicMock()
    mock_kafka_producer.start = AsyncMock()
    mock_kafka_producer.stop = AsyncMock()

    # Mock Kafka consumer
    mock_kafka_consumer = MagicMock()
    mock_kafka_consumer.start = AsyncMock()
    mock_kafka_consumer.stop = AsyncMock()
    mock_kafka_consumer.consume_messages = MagicMock(
        return_value=AsyncMock()  # Returns a coroutine that can be used in create_task
    )

    app.dependency_overrides[get_db] = override_get_db

    with patch("app.db.mongodb.mongodb", mock_mongodb), \
         patch("app.db.redis.redis_client", mock_redis), \
         patch("app.services.kafka_producer.kafka_producer", mock_kafka_producer), \
         patch("app.services.kafka_consumer.deals_consumer", mock_kafka_consumer):
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
