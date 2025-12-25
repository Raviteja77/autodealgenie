"""
Unit tests for user preferences service
Tests CRUD operations with mocked MongoDB
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.user_preferences_service import (
    UserPreference,
    UserPreferencesService,
)


@pytest.fixture
def service():
    """Create a UserPreferencesService instance"""
    return UserPreferencesService()


@pytest.fixture
def mock_collection():
    """Create a mock MongoDB collection"""
    collection = MagicMock()
    collection.insert_one = AsyncMock()
    collection.find = MagicMock()
    collection.find_one = AsyncMock()
    collection.delete_many = AsyncMock()
    return collection


@pytest.fixture
def sample_preferences():
    """Sample user preferences data"""
    return {
        "makes": ["Toyota", "Honda"],
        "budget_range": {"min": 20000, "max": 35000},
        "year_range": {"min": 2020, "max": 2024},
        "body_types": ["sedan", "suv"],
        "features": ["sunroof", "leather seats", "backup camera"],
    }


class TestUserPreference:
    """Tests for UserPreference document class"""

    def test_user_preference_creation(self):
        """Test creating a UserPreference document"""
        preferences = {
            "makes": ["Toyota"],
            "budget_range": {"min": 20000, "max": 30000},
            "year_range": {"min": 2020, "max": 2023},
            "body_types": ["sedan"],
            "features": ["sunroof"],
        }
        user_pref = UserPreference(user_id="user123", preferences=preferences)

        assert user_pref["user_id"] == "user123"
        assert user_pref["preferences"] == preferences
        assert "created_at" in user_pref
        assert "updated_at" in user_pref
        assert isinstance(user_pref["created_at"], datetime)
        assert isinstance(user_pref["updated_at"], datetime)

    def test_user_preference_with_custom_dates(self):
        """Test creating UserPreference with custom dates"""
        created = datetime(2024, 1, 1, tzinfo=UTC)
        updated = datetime(2024, 1, 15, tzinfo=UTC)
        preferences = {"makes": ["Honda"], "budget_range": {"min": 15000, "max": 25000}}

        user_pref = UserPreference(
            user_id="user456",
            preferences=preferences,
            created_at=created,
            updated_at=updated,
        )

        assert user_pref["created_at"] == created
        assert user_pref["updated_at"] == updated


class TestSaveUserPreferences:
    """Tests for save_user_preferences method"""

    @pytest.mark.asyncio
    async def test_save_user_preferences_full(self, service, mock_collection, sample_preferences):
        """Test saving user preferences with all fields"""
        service._collection = mock_collection

        await service.save_user_preferences(
            user_id="user123",
            makes=sample_preferences["makes"],
            budget_range=sample_preferences["budget_range"],
            year_range=sample_preferences["year_range"],
            body_types=sample_preferences["body_types"],
            features=sample_preferences["features"],
        )

        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]

        assert call_args["user_id"] == "user123"
        assert call_args["preferences"]["makes"] == sample_preferences["makes"]
        assert call_args["preferences"]["budget_range"] == sample_preferences["budget_range"]
        assert call_args["preferences"]["year_range"] == sample_preferences["year_range"]
        assert call_args["preferences"]["body_types"] == sample_preferences["body_types"]
        assert call_args["preferences"]["features"] == sample_preferences["features"]
        assert "created_at" in call_args
        assert "updated_at" in call_args

    @pytest.mark.asyncio
    async def test_save_user_preferences_minimal(self, service, mock_collection):
        """Test saving user preferences with minimal data"""
        service._collection = mock_collection

        await service.save_user_preferences(user_id="user456")

        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]

        assert call_args["user_id"] == "user456"
        assert call_args["preferences"]["makes"] == []
        assert call_args["preferences"]["budget_range"] == {"min": 0, "max": 0}
        assert call_args["preferences"]["year_range"] == {"min": 0, "max": 0}
        assert call_args["preferences"]["body_types"] == []
        assert call_args["preferences"]["features"] == []

    @pytest.mark.asyncio
    async def test_save_user_preferences_partial(self, service, mock_collection):
        """Test saving user preferences with partial data"""
        service._collection = mock_collection

        await service.save_user_preferences(
            user_id="user789",
            makes=["Ford", "Chevrolet"],
            features=["4WD", "towing package"],
        )

        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]

        assert call_args["preferences"]["makes"] == ["Ford", "Chevrolet"]
        assert call_args["preferences"]["features"] == ["4WD", "towing package"]
        assert call_args["preferences"]["budget_range"] == {"min": 0, "max": 0}


class TestGetUserPreferences:
    """Tests for get_user_preferences method"""

    @pytest.mark.asyncio
    async def test_get_user_preferences_found(self, service, mock_collection, sample_preferences):
        """Test retrieving existing user preferences"""
        service._collection = mock_collection

        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {
                    "user_id": "user123",
                    "preferences": sample_preferences,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC),
                }
            ]
        )
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_collection.find.return_value = mock_cursor

        result = await service.get_user_preferences("user123")

        mock_collection.find.assert_called_once_with({"user_id": "user123"})
        mock_cursor.sort.assert_called_once_with("created_at", -1)
        assert len(result) == 1
        assert result[0]["user_id"] == "user123"
        assert result[0]["preferences"] == sample_preferences

    @pytest.mark.asyncio
    async def test_get_user_preferences_not_found(self, service, mock_collection):
        """Test retrieving preferences for non-existent user"""
        service._collection = mock_collection

        # Mock cursor with empty results
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(return_value=[])
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_collection.find.return_value = mock_cursor

        result = await service.get_user_preferences("nonexistent")

        assert result == []

    @pytest.mark.asyncio
    async def test_get_user_preferences_multiple_results(self, service, mock_collection):
        """Test retrieving multiple preference records"""
        service._collection = mock_collection

        # Mock cursor with multiple results
        now = datetime.now(UTC)
        mock_cursor = MagicMock()
        mock_cursor.to_list = AsyncMock(
            return_value=[
                {
                    "user_id": "user123",
                    "preferences": {"makes": ["Toyota"]},
                    "created_at": now,
                    "updated_at": now,
                },
                {
                    "user_id": "user123",
                    "preferences": {"makes": ["Honda"]},
                    "created_at": now - timedelta(days=1),
                    "updated_at": now - timedelta(days=1),
                },
            ]
        )
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_collection.find.return_value = mock_cursor

        result = await service.get_user_preferences("user123")

        assert len(result) == 2
        assert result[0]["preferences"]["makes"] == ["Toyota"]
        assert result[1]["preferences"]["makes"] == ["Honda"]


class TestUpdateUserPreferences:
    """Tests for update_user_preferences method"""

    @pytest.mark.asyncio
    async def test_update_user_preferences_with_existing(
        self, service, mock_collection, sample_preferences
    ):
        """Test updating existing user preferences"""
        service._collection = mock_collection

        # Mock existing preference
        existing_doc = {
            "user_id": "user123",
            "preferences": sample_preferences,
            "created_at": datetime.now(UTC) - timedelta(days=1),
            "updated_at": datetime.now(UTC) - timedelta(days=1),
        }
        mock_collection.find_one.return_value = existing_doc

        # Update with new data
        new_makes = ["BMW", "Mercedes"]
        await service.update_user_preferences(user_id="user123", makes=new_makes)

        mock_collection.find_one.assert_called_once()
        mock_collection.insert_one.assert_called_once()

        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["user_id"] == "user123"
        assert call_args["preferences"]["makes"] == new_makes
        # Other fields should be preserved
        assert call_args["preferences"]["budget_range"] == sample_preferences["budget_range"]
        assert call_args["preferences"]["features"] == sample_preferences["features"]

    @pytest.mark.asyncio
    async def test_update_user_preferences_no_existing(self, service, mock_collection):
        """Test updating when no existing preferences"""
        service._collection = mock_collection
        mock_collection.find_one.return_value = None

        await service.update_user_preferences(
            user_id="newuser",
            makes=["Nissan"],
            budget_range={"min": 15000, "max": 25000},
        )

        mock_collection.insert_one.assert_called_once()
        call_args = mock_collection.insert_one.call_args[0][0]

        assert call_args["user_id"] == "newuser"
        assert call_args["preferences"]["makes"] == ["Nissan"]
        assert call_args["preferences"]["budget_range"] == {"min": 15000, "max": 25000}

    @pytest.mark.asyncio
    async def test_update_user_preferences_multiple_fields(self, service, mock_collection):
        """Test updating multiple fields at once"""
        service._collection = mock_collection

        existing_doc = {
            "user_id": "user123",
            "preferences": {
                "makes": ["Toyota"],
                "budget_range": {"min": 20000, "max": 30000},
                "year_range": {"min": 2020, "max": 2023},
                "body_types": ["sedan"],
                "features": ["sunroof"],
            },
        }
        mock_collection.find_one.return_value = existing_doc

        await service.update_user_preferences(
            user_id="user123",
            makes=["Honda", "Mazda"],
            year_range={"min": 2022, "max": 2024},
            features=["leather", "navigation"],
        )

        call_args = mock_collection.insert_one.call_args[0][0]
        assert call_args["preferences"]["makes"] == ["Honda", "Mazda"]
        assert call_args["preferences"]["year_range"] == {"min": 2022, "max": 2024}
        assert call_args["preferences"]["features"] == ["leather", "navigation"]
        # Unchanged fields should remain
        assert call_args["preferences"]["budget_range"] == {"min": 20000, "max": 30000}
        assert call_args["preferences"]["body_types"] == ["sedan"]


class TestDeleteOlderPreferences:
    """Tests for delete_older_preferences method"""

    @pytest.mark.asyncio
    async def test_delete_older_preferences_default_days(self, service, mock_collection):
        """Test deleting preferences older than 30 days (default)"""
        service._collection = mock_collection

        # Mock delete result
        delete_result = MagicMock()
        delete_result.deleted_count = 5
        mock_collection.delete_many.return_value = delete_result

        result = await service.delete_older_preferences()

        mock_collection.delete_many.assert_called_once()
        call_args = mock_collection.delete_many.call_args[0][0]

        # Verify the date filter is approximately 30 days ago
        cutoff = call_args["created_at"]["$lt"]
        expected_cutoff = datetime.now(UTC) - timedelta(days=30)
        time_diff = abs((cutoff - expected_cutoff).total_seconds())
        assert time_diff < 1  # Should be within 1 second

        assert result == 5

    @pytest.mark.asyncio
    async def test_delete_older_preferences_custom_days(self, service, mock_collection):
        """Test deleting preferences older than custom number of days"""
        service._collection = mock_collection

        delete_result = MagicMock()
        delete_result.deleted_count = 10
        mock_collection.delete_many.return_value = delete_result

        result = await service.delete_older_preferences(days=60)

        mock_collection.delete_many.assert_called_once()
        call_args = mock_collection.delete_many.call_args[0][0]

        # Verify the date filter is approximately 60 days ago
        cutoff = call_args["created_at"]["$lt"]
        expected_cutoff = datetime.now(UTC) - timedelta(days=60)
        time_diff = abs((cutoff - expected_cutoff).total_seconds())
        assert time_diff < 1

        assert result == 10

    @pytest.mark.asyncio
    async def test_delete_older_preferences_none_deleted(self, service, mock_collection):
        """Test when no preferences are old enough to delete"""
        service._collection = mock_collection

        delete_result = MagicMock()
        delete_result.deleted_count = 0
        mock_collection.delete_many.return_value = delete_result

        result = await service.delete_older_preferences(days=90)

        assert result == 0

    @pytest.mark.asyncio
    async def test_delete_older_preferences_seven_days(self, service, mock_collection):
        """Test deleting preferences older than 7 days"""
        service._collection = mock_collection

        delete_result = MagicMock()
        delete_result.deleted_count = 3
        mock_collection.delete_many.return_value = delete_result

        result = await service.delete_older_preferences(days=7)

        call_args = mock_collection.delete_many.call_args[0][0]
        cutoff = call_args["created_at"]["$lt"]
        expected_cutoff = datetime.now(UTC) - timedelta(days=7)
        time_diff = abs((cutoff - expected_cutoff).total_seconds())
        assert time_diff < 1

        assert result == 3


class TestServiceInitialization:
    """Tests for service initialization and collection property"""

    def test_service_initialization(self):
        """Test that service initializes correctly"""
        service = UserPreferencesService()
        assert service._collection is None
        assert service.COLLECTION_NAME == "user_preferences"

    @patch("app.services.user_preferences_service.mongodb")
    def test_collection_property_lazy_init(self, mock_mongodb):
        """Test that collection property lazy initializes"""
        mock_collection = MagicMock()
        mock_mongodb.get_collection.return_value = mock_collection

        service = UserPreferencesService()
        assert service._collection is None

        # Access property
        collection = service.collection

        mock_mongodb.get_collection.assert_called_once_with("user_preferences")
        assert collection == mock_collection
        assert service._collection == mock_collection

    @patch("app.services.user_preferences_service.mongodb")
    def test_collection_property_cached(self, mock_mongodb):
        """Test that collection property is cached after first access"""
        mock_collection = MagicMock()
        mock_mongodb.get_collection.return_value = mock_collection

        service = UserPreferencesService()

        # Access property multiple times
        collection1 = service.collection
        collection2 = service.collection

        # Should only call get_collection once
        mock_mongodb.get_collection.assert_called_once()
        assert collection1 == collection2
