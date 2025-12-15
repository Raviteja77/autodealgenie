"""
Tests for search history repository
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.repositories.search_history_repository import SearchHistoryRepository


@pytest.mark.asyncio
async def test_create_search_record():
    """Test creating a search history record"""
    repo = SearchHistoryRepository()

    # Mock MongoDB collection
    mock_collection = AsyncMock()
    mock_result = MagicMock()
    mock_result.inserted_id = "507f1f77bcf86cd799439011"
    mock_collection.insert_one = AsyncMock(return_value=mock_result)

    search_criteria = {"make": "Toyota", "model": "RAV4"}
    top_vehicles = [{"vin": "123", "make": "Toyota", "model": "RAV4"}]

    with patch(
        "app.repositories.search_history_repository.mongodb.get_collection",
        return_value=mock_collection,
    ):
        record_id = await repo.create_search_record(
            user_id=1,
            search_criteria=search_criteria,
            result_count=10,
            top_vehicles=top_vehicles,
        )

        assert record_id == "507f1f77bcf86cd799439011"
        mock_collection.insert_one.assert_called_once()

        # Verify the document structure
        call_args = mock_collection.insert_one.call_args
        document = call_args[0][0]
        assert document["user_id"] == 1
        assert document["search_criteria"] == search_criteria
        assert document["result_count"] == 10
        assert document["top_vehicles"] == top_vehicles
        assert isinstance(document["timestamp"], datetime)


@pytest.mark.asyncio
async def test_get_user_history():
    """Test retrieving user search history"""
    repo = SearchHistoryRepository()

    # Mock MongoDB collection
    mock_collection = AsyncMock()
    mock_cursor = MagicMock()

    # Mock async iteration
    mock_records = [
        {
            "_id": "507f1f77bcf86cd799439011",
            "user_id": 1,
            "search_criteria": {"make": "Toyota"},
            "result_count": 5,
            "timestamp": datetime.utcnow(),
        },
        {
            "_id": "507f1f77bcf86cd799439012",
            "user_id": 1,
            "search_criteria": {"make": "Honda"},
            "result_count": 3,
            "timestamp": datetime.utcnow(),
        },
    ]

    async def async_iterator():
        for record in mock_records:
            yield record

    mock_cursor.__aiter__ = lambda self: async_iterator()
    mock_collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = (
        mock_cursor
    )

    with patch(
        "app.repositories.search_history_repository.mongodb.get_collection",
        return_value=mock_collection,
    ):
        records = await repo.get_user_history(user_id=1, limit=10, skip=0)

        assert len(records) == 2
        assert records[0]["_id"] == "507f1f77bcf86cd799439011"
        assert records[1]["_id"] == "507f1f77bcf86cd799439012"


@pytest.mark.asyncio
async def test_get_popular_searches():
    """Test retrieving popular searches"""
    repo = SearchHistoryRepository()

    # Mock MongoDB collection
    mock_collection = AsyncMock()

    # Mock aggregation results
    mock_results = [
        {"_id": {"make": "Toyota", "model": "RAV4"}, "count": 15},
        {"_id": {"make": "Honda", "model": "Civic"}, "count": 10},
    ]

    async def async_aggregation_iterator():
        for result in mock_results:
            yield result

    mock_collection.aggregate.return_value.__aiter__ = async_aggregation_iterator

    with patch(
        "app.repositories.search_history_repository.mongodb.get_collection",
        return_value=mock_collection,
    ):
        popular = await repo.get_popular_searches(limit=5, days=7)

        assert len(popular) == 2
        assert popular[0]["make"] == "Toyota"
        assert popular[0]["model"] == "RAV4"
        assert popular[0]["search_count"] == 15


@pytest.mark.asyncio
async def test_delete_user_history():
    """Test deleting user search history"""
    repo = SearchHistoryRepository()

    # Mock MongoDB collection
    mock_collection = AsyncMock()
    mock_result = MagicMock()
    mock_result.deleted_count = 5
    mock_collection.delete_many = AsyncMock(return_value=mock_result)

    with patch(
        "app.repositories.search_history_repository.mongodb.get_collection",
        return_value=mock_collection,
    ):
        deleted_count = await repo.delete_user_history(user_id=1)

        assert deleted_count == 5
        mock_collection.delete_many.assert_called_once_with({"user_id": 1})
