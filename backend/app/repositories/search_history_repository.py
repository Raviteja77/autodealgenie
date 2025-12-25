"""
Repository for search history operations in MongoDB
Stores all car search queries for analytics
"""

from datetime import datetime
from typing import Any

from app.db.mongodb import mongodb


class SearchHistoryRepository:
    """Repository for managing search history in MongoDB"""

    COLLECTION_NAME = "search_history"

    def __init__(self):
        """Initialize repository"""
        pass

    async def create_search_record(
        self,
        user_id: int | None,
        search_criteria: dict[str, Any],
        result_count: int,
        top_vehicles: list[dict[str, Any]],
    ) -> str:
        """
        Create a search history record

        Args:
            user_id: User ID (None for anonymous searches)
            search_criteria: Search criteria used
            result_count: Number of results found
            top_vehicles: List of top vehicle recommendations

        Returns:
            str: Inserted document ID
        """
        collection = mongodb.get_collection(self.COLLECTION_NAME)

        document = {
            "user_id": user_id,
            "search_criteria": search_criteria,
            "result_count": result_count,
            "top_vehicles": top_vehicles,
            "timestamp": datetime.utcnow(),
            "session_id": None,  # Can be added for session tracking
        }

        result = await collection.insert_one(document)
        return str(result.inserted_id)

    async def get_user_history(
        self, user_id: int, limit: int = 50, skip: int = 0
    ) -> list[dict[str, Any]]:
        """
        Get search history for a user

        Args:
            user_id: User ID
            limit: Maximum number of records to return
            skip: Number of records to skip (for pagination)

        Returns:
            List of search history records
        """
        collection = mongodb.get_collection(self.COLLECTION_NAME)

        cursor = (
            collection.find({"user_id": user_id})
            .sort("timestamp", -1)
            .skip(skip)
            .limit(limit)
        )

        records = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            records.append(doc)

        return records

    async def get_popular_searches(
        self, limit: int = 10, days: int = 7
    ) -> list[dict[str, Any]]:
        """
        Get popular search criteria from recent history

        Args:
            limit: Maximum number of results
            days: Number of days to look back

        Returns:
            List of popular search patterns
        """
        collection = mongodb.get_collection(self.COLLECTION_NAME)

        # Calculate cutoff date
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Aggregate popular makes
        pipeline = [
            {"$match": {"timestamp": {"$gte": cutoff_date}}},
            {
                "$group": {
                    "_id": {
                        "make": "$search_criteria.make",
                        "model": "$search_criteria.model",
                    },
                    "count": {"$sum": 1},
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]

        results = []
        async for doc in collection.aggregate(pipeline):
            results.append(
                {
                    "make": doc["_id"]["make"],
                    "model": doc["_id"]["model"],
                    "search_count": doc["count"],
                }
            )

        return results

    async def delete_user_history(self, user_id: int) -> int:
        """
        Delete all search history for a user

        Args:
            user_id: User ID

        Returns:
            Number of records deleted
        """
        collection = mongodb.get_collection(self.COLLECTION_NAME)
        result = await collection.delete_many({"user_id": user_id})
        return result.deleted_count


# Singleton instance
search_history_repository = SearchHistoryRepository()
