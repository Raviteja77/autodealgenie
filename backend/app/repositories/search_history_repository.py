"""
Repository for search history operations in PostgreSQL
Previously used MongoDB, now using PostgreSQL JSONB
"""

from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.jsonb_data import SearchHistory


class SearchHistoryRepository:
    """Repository for managing search history in PostgreSQL"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_search_record(
        self,
        user_id: int | None,
        search_criteria: dict[str, Any],
        result_count: int,
        top_vehicles: list[dict[str, Any]],
        session_id: str | None = None,
    ) -> SearchHistory:
        """
        Create a search history record

        Args:
            user_id: User ID (None for anonymous searches)
            search_criteria: Search criteria used
            result_count: Number of results found
            top_vehicles: List of top vehicle recommendations
            session_id: Session identifier for tracking

        Returns:
            SearchHistory: Created record
        """
        record = SearchHistory(
            user_id=user_id,
            search_criteria=search_criteria,
            result_count=result_count,
            top_vehicles=top_vehicles,
            session_id=session_id,
        )

        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record

    async def get_user_history(
        self, user_id: int, limit: int = 50, skip: int = 0
    ) -> list[SearchHistory]:
        """
        Get search history for a user

        Args:
            user_id: User ID
            limit: Maximum number of records to return
            skip: Number of records to skip (for pagination)

        Returns:
            List of search history records
        """
        result = await self.db.execute(
            select(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .order_by(desc(SearchHistory.timestamp))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_popular_searches(self, limit: int = 10, days: int = 7) -> list[dict[str, Any]]:
        """
        Get popular search criteria from recent history

        Args:
            limit: Maximum number of results
            days: Number of days to look back

        Returns:
            List of popular search patterns
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Query for popular make/model combinations
        # Note: PostgreSQL JSONB queries use ->> for text extraction
        result = await self.db.execute(
            select(
                SearchHistory.search_criteria["make"].astext.label("make"),
                SearchHistory.search_criteria["model"].astext.label("model"),
                func.count().label("count"),
            )
            .filter(SearchHistory.timestamp >= cutoff_date)
            .group_by(
                SearchHistory.search_criteria["make"].astext,
                SearchHistory.search_criteria["model"].astext,
            )
            .order_by(desc("count"))
            .limit(limit)
        )
        results = result.all()

        return [
            {
                "make": row.make,
                "model": row.model,
                "search_count": row.count,
            }
            for row in results
        ]

    async def delete_user_history(self, user_id: int) -> int:
        """
        Delete all search history for a user

        Args:
            user_id: User ID

        Returns:
            Number of records deleted
        """
        result = await self.db.execute(
            select(SearchHistory).filter(SearchHistory.user_id == user_id)
        )
        history_to_delete = result.scalars().all()
        for history in history_to_delete:
            await self.db.delete(history)
        await self.db.commit()
        return len(history_to_delete)


# Factory function to create repository with db session
def get_search_history_repository(db: AsyncSession) -> SearchHistoryRepository:
    """Factory function to create repository with db session"""
    return SearchHistoryRepository(db)
