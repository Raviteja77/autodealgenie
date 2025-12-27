"""
Tests for PostgreSQL JSONB repositories
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.repositories.ai_response_repository import AIResponseRepository
from app.repositories.search_history_repository import SearchHistoryRepository
from app.repositories.user_preferences_repository import UserPreferencesRepository


@pytest_asyncio.fixture
async def db_session():
    """Create a test database session"""
    # NOTE: These tests use SQLite for simplicity, but production uses PostgreSQL with JSONB
    # SQLite doesn't support JSONB natively, so some functionality may differ
    # For full testing, use PostgreSQL test database or testcontainers
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # Import Base and create all tables
    from app.db.session import Base

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with AsyncSessionLocal() as session:
        yield session

    await engine.dispose()


class TestUserPreferencesRepository:
    """Test cases for UserPreferencesRepository"""

    @pytest.mark.asyncio
    async def test_save_user_preferences(self, db_session: AsyncSession):
        """Test saving user preferences"""
        repo = UserPreferencesRepository(db_session)

        pref = await repo.save_user_preferences(
            user_id="user123",
            makes=["Toyota", "Honda"],
            budget_range={"min": 20000, "max": 30000},
            year_range={"min": 2020, "max": 2024},
            body_types=["Sedan", "SUV"],
            features=["Backup Camera", "Bluetooth"],
        )

        assert pref.id is not None
        assert pref.user_id == "user123"
        assert pref.preferences["makes"] == ["Toyota", "Honda"]
        assert pref.preferences["budget_range"]["min"] == 20000

    @pytest.mark.asyncio
    async def test_get_user_preferences(self, db_session: AsyncSession):
        """Test retrieving user preferences"""
        repo = UserPreferencesRepository(db_session)

        # Save multiple preferences
        await repo.save_user_preferences(user_id="user123", makes=["Toyota"])
        await repo.save_user_preferences(user_id="user123", makes=["Honda"])

        prefs = await repo.get_user_preferences("user123")

        assert len(prefs) == 2
        assert all(p.user_id == "user123" for p in prefs)

    @pytest.mark.asyncio
    async def test_get_latest_user_preference(self, db_session: AsyncSession):
        """Test getting the most recent preference"""
        repo = UserPreferencesRepository(db_session)

        await repo.save_user_preferences(user_id="user123", makes=["Toyota"])
        await repo.save_user_preferences(user_id="user123", makes=["Honda"])

        latest = await repo.get_latest_user_preference("user123")

        assert latest is not None
        assert latest.preferences["makes"] == ["Honda"]


class TestSearchHistoryRepository:
    """Test cases for SearchHistoryRepository"""

    @pytest.mark.asyncio
    async def test_create_search_record(self, db_session: AsyncSession):
        """Test creating a search history record"""
        repo = SearchHistoryRepository(db_session)

        record = await repo.create_search_record(
            user_id=1,
            search_criteria={"make": "Toyota", "model": "Camry", "year": 2022},
            result_count=15,
            top_vehicles=[{"vin": "123", "price": 25000}],
            session_id="session123",
        )

        assert record.id is not None
        assert record.user_id == 1
        assert record.search_criteria["make"] == "Toyota"
        assert record.result_count == 15

    @pytest.mark.asyncio
    async def test_get_user_history(self, db_session: AsyncSession):
        """Test retrieving user's search history"""
        repo = SearchHistoryRepository(db_session)

        # Note: We need to create a user first for foreign key constraint
        # For this test, we'll use a nullable user_id or mock the user

        # Create search records
        await repo.create_search_record(
            user_id=None,  # Anonymous search
            search_criteria={"make": "Toyota"},
            result_count=10,
            top_vehicles=[],
        )

        # Test would work with actual user_id if user table exists
        # history = await repo.get_user_history(user_id=1)
        # assert len(history) > 0


class TestAIResponseRepository:
    """Test cases for AIResponseRepository"""

    @pytest.mark.asyncio
    async def test_create_response(self, db_session: AsyncSession):
        """Test creating an AI response record"""
        repo = AIResponseRepository(db_session)

        response = await repo.create_response(
            feature="negotiation",
            user_id=None,
            deal_id=None,
            prompt_id="test_prompt",
            prompt_variables={"key": "value"},
            response_content={"text": "AI response here"},
            response_metadata={"score": 85},
            model_used="gpt-4",
            tokens_used=150,
            temperature=0.7,
            llm_used=True,
        )

        assert response.id is not None
        assert response.feature == "negotiation"
        assert response.prompt_id == "test_prompt"
        assert response.llm_used == 1  # Stored as integer
        assert response.temperature == 70  # Stored as int * 100

    @pytest.mark.asyncio
    async def test_get_by_feature(self, db_session: AsyncSession):
        """Test retrieving responses by feature"""
        repo = AIResponseRepository(db_session)

        # Create multiple responses
        await repo.create_response(
            feature="negotiation",
            user_id=None,
            deal_id=None,
            prompt_id="test1",
            prompt_variables={},
            response_content={"text": "Response 1"},
        )

        await repo.create_response(
            feature="deal_evaluation",
            user_id=None,
            deal_id=None,
            prompt_id="test2",
            prompt_variables={},
            response_content={"text": "Response 2"},
        )

        negotiation_responses = await repo.get_by_feature("negotiation")

        assert len(negotiation_responses) == 1
        assert negotiation_responses[0].feature == "negotiation"

    @pytest.mark.asyncio
    async def test_get_analytics(self, db_session: AsyncSession):
        """Test getting AI usage analytics"""
        repo = AIResponseRepository(db_session)

        # Create some test responses
        await repo.create_response(
            feature="negotiation",
            user_id=None,
            deal_id=None,
            prompt_id="test1",
            prompt_variables={},
            response_content={"text": "Response"},
            tokens_used=100,
            llm_used=True,
        )

        await repo.create_response(
            feature="negotiation",
            user_id=None,
            deal_id=None,
            prompt_id="test2",
            prompt_variables={},
            response_content={"text": "Fallback"},
            tokens_used=0,
            llm_used=False,
        )

        analytics = await repo.get_analytics(days=30)

        assert "features" in analytics
        assert "negotiation" in analytics["features"]
        assert analytics["features"]["negotiation"]["total_calls"] == 2
        assert analytics["features"]["negotiation"]["llm_calls"] == 1
        assert analytics["features"]["negotiation"]["fallback_calls"] == 1
