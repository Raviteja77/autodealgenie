"""
Repository for MarketCheck query history and cached data

This repository manages persistent storage of MarketCheck API queries
and responses in PostgreSQL JSONB for analytics and caching purposes.
Previously used MongoDB, now using PostgreSQL for consistency.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.jsonb_data import MarketCheckQuery

logger = logging.getLogger(__name__)


class MarketCheckQueryRepository:
    """
    Repository for storing MarketCheck API query history in PostgreSQL

    This stores:
    - Search queries and their parameters
    - API response metadata (num_found, timestamp)
    - Query performance metrics
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize repository with PostgreSQL AsyncSession

        Args:
            db: AsyncSession database instance
        """
        self.db = db

    async def save_query(
        self,
        query_type: str,
        params: dict[str, Any],
        response_summary: dict[str, Any],
        user_id: int | None = None,
    ) -> int:
        """
        Save a MarketCheck query to the database

        Args:
            query_type: Type of query ('search', 'price', 'vin', 'mds')
            params: Query parameters
            response_summary: Summary of API response (e.g., num_found, status)
            user_id: Optional user ID who made the query

        Returns:
            Query record ID
        """
        try:
            record = MarketCheckQuery(
                query_type=query_type,
                params=params,
                response_summary=response_summary,
                user_id=user_id,
            )

            self.db.add(record)
            await self.db.commit()
            await self.db.refresh(record)
            logger.debug(f"Saved MarketCheck query: {query_type} -> {record.id}")
            return record.id

        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error saving MarketCheck query: {e}", exc_info=True)
            raise

    async def get_query_history(
        self,
        user_id: int | None = None,
        query_type: str | None = None,
        limit: int = 50,
        skip: int = 0,
    ) -> list[MarketCheckQuery]:
        """
        Get query history with optional filters

        Args:
            user_id: Filter by user ID
            query_type: Filter by query type
            limit: Maximum number of records
            skip: Number of records to skip (pagination)

        Returns:
            List of query records
        """
        try:
            query = select(MarketCheckQuery)

            if user_id is not None:
                query = query.filter(MarketCheckQuery.user_id == user_id)
            if query_type:
                query = query.filter(MarketCheckQuery.query_type == query_type)

            query = query.order_by(desc(MarketCheckQuery.timestamp)).offset(skip).limit(limit)

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting query history: {e}", exc_info=True)
            raise

    async def get_recent_searches(
        self, user_id: int | None = None, hours: int = 24, limit: int = 10
    ) -> list[MarketCheckQuery]:
        """
        Get recent search queries

        Args:
            user_id: Optional user ID filter
            hours: Number of hours to look back
            limit: Maximum number of records

        Returns:
            List of recent search queries
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            query = (
                select(MarketCheckQuery)
                .filter(MarketCheckQuery.query_type == "search")
                .filter(MarketCheckQuery.timestamp >= cutoff_time)
            )

            if user_id is not None:
                query = query.filter(MarketCheckQuery.user_id == user_id)

            query = query.order_by(desc(MarketCheckQuery.timestamp)).limit(limit)

            result = await self.db.execute(query)
            return result.scalars().all()

        except Exception as e:
            logger.error(f"Error getting recent searches: {e}", exc_info=True)
            raise

    async def get_query_stats(self, user_id: int | None = None, days: int = 7) -> dict[str, Any]:
        """
        Get query statistics

        Args:
            user_id: Optional user ID filter
            days: Number of days to analyze

        Returns:
            Dictionary with query statistics
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(days=days)
            query = select(
                MarketCheckQuery.query_type, func.count(MarketCheckQuery.id).label("count")
            ).filter(MarketCheckQuery.timestamp >= cutoff_time)

            if user_id is not None:
                query = query.filter(MarketCheckQuery.user_id == user_id)

            query = query.group_by(MarketCheckQuery.query_type)

            result = await self.db.execute(query)
            stats = {row[0]: row[1] for row in result.all()}

            return {
                "period_days": days,
                "query_counts": stats,
                "total_queries": sum(stats.values()),
            }

        except Exception as e:
            logger.error(f"Error getting query stats: {e}", exc_info=True)
            raise
