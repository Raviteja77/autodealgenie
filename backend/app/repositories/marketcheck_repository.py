"""
Repository for MarketCheck query history and cached data

This repository manages persistent storage of MarketCheck API queries
and responses in MongoDB for analytics and caching purposes.
"""

import logging
from datetime import datetime
from typing import Any

from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)


class MarketCheckQueryRepository:
    """
    Repository for storing MarketCheck API query history in MongoDB

    This stores:
    - Search queries and their parameters
    - API response metadata (num_found, timestamp)
    - Query performance metrics
    """

    def __init__(self, db: AsyncIOMotorDatabase):
        """
        Initialize repository with MongoDB database

        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.collection = db.marketcheck_queries

    async def save_query(
        self,
        query_type: str,
        params: dict[str, Any],
        response_summary: dict[str, Any],
        user_id: int | None = None,
    ) -> str:
        """
        Save a MarketCheck query to the database

        Args:
            query_type: Type of query ('search', 'price', 'vin', 'mds')
            params: Query parameters
            response_summary: Summary of API response (e.g., num_found, status)
            user_id: Optional user ID who made the query

        Returns:
            Query document ID
        """
        try:
            document = {
                "query_type": query_type,
                "params": params,
                "response_summary": response_summary,
                "user_id": user_id,
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow(),
            }

            result = await self.collection.insert_one(document)
            logger.debug(f"Saved MarketCheck query: {query_type} -> {result.inserted_id}")
            return str(result.inserted_id)

        except Exception as e:
            logger.error(f"Error saving MarketCheck query: {e}", exc_info=True)
            raise

    async def get_query_history(
        self,
        user_id: int | None = None,
        query_type: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """
        Get query history with optional filtering

        Args:
            user_id: Filter by user ID
            query_type: Filter by query type
            limit: Maximum number of results

        Returns:
            List of query documents
        """
        try:
            query: dict[str, Any] = {}

            if user_id is not None:
                query["user_id"] = user_id
            if query_type:
                query["query_type"] = query_type

            cursor = self.collection.find(query).sort("timestamp", -1).limit(limit)

            results = []
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                results.append(doc)

            logger.debug(
                f"Retrieved {len(results)} MarketCheck queries "
                f"(user_id={user_id}, type={query_type})"
            )
            return results

        except Exception as e:
            logger.error(f"Error getting query history: {e}", exc_info=True)
            raise

    async def get_query_stats(self, query_type: str | None = None) -> dict[str, Any]:
        """
        Get aggregate statistics for MarketCheck queries

        Args:
            query_type: Optional filter by query type

        Returns:
            Dictionary with statistics (total_queries, queries_by_type, etc.)
        """
        try:
            match_stage: dict[str, Any] = {}
            if query_type:
                match_stage["query_type"] = query_type

            pipeline = [
                {"$match": match_stage} if match_stage else {"$match": {}},
                {
                    "$group": {
                        "_id": "$query_type",
                        "count": {"$sum": 1},
                        "latest": {"$max": "$timestamp"},
                    }
                },
            ]

            cursor = self.collection.aggregate(pipeline)
            stats_by_type = {}
            total = 0

            async for doc in cursor:
                stats_by_type[doc["_id"]] = {
                    "count": doc["count"],
                    "latest": doc["latest"],
                }
                total += doc["count"]

            return {
                "total_queries": total,
                "queries_by_type": stats_by_type,
            }

        except Exception as e:
            logger.error(f"Error getting query stats: {e}", exc_info=True)
            raise


class VINHistoryRepository:
    """
    Repository for storing VIN lookup history in PostgreSQL

    This stores comprehensive VIN details and lookup history
    for analytics and caching purposes.
    """

    def __init__(self, db):
        """
        Initialize repository with database session

        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        # TODO: Create VINHistory model if needed

    def save_vin_lookup(
        self,
        vin: str,
        details: dict[str, Any],
        user_id: int | None = None,
    ) -> int:
        """
        Save VIN lookup to database

        Args:
            vin: Vehicle Identification Number
            details: VIN details from MarketCheck
            user_id: Optional user ID who requested the lookup

        Returns:
            Record ID
        """
        # TODO: Implement once VINHistory model is created
        logger.debug(f"VIN lookup saved: {vin} (user_id={user_id})")
        return 0

    def get_vin_history(self, vin: str, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get lookup history for a VIN

        Args:
            vin: Vehicle Identification Number
            limit: Maximum number of records

        Returns:
            List of VIN lookup records
        """
        # TODO: Implement once VINHistory model is created
        logger.debug(f"Retrieved VIN history: {vin}")
        return []
