"""
Repository for saved search operations in PostgreSQL
"""

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import SavedSearch


class SavedSearchRepository:
    """Repository for managing saved searches"""

    async def create(self, db: AsyncSession, user_id: int, search_data: dict) -> SavedSearch:
        """
        Create a new saved search

        Args:
            db: Database session
            user_id: User ID
            search_data: Search criteria data

        Returns:
            SavedSearch: Created saved search
        """
        saved_search = SavedSearch(user_id=user_id, **search_data)
        db.add(saved_search)
        await db.commit()
        await db.refresh(saved_search)
        return saved_search

    async def get_by_id(self, db: AsyncSession, search_id: int, user_id: int) -> SavedSearch | None:
        """
        Get a saved search by ID

        Args:
            db: Database session
            search_id: Search ID
            user_id: User ID (for authorization)

        Returns:
            Optional[SavedSearch]: Saved search or None
        """
        result = await db.execute(
            select(SavedSearch)
            .filter(and_(SavedSearch.id == search_id, SavedSearch.user_id == user_id))
        )
        return result.scalar_one_or_none()

    async def get_user_searches(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[SavedSearch]:
        """
        Get all saved searches for a user

        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            list[SavedSearch]: List of saved searches
        """
        result = await db.execute(
            select(SavedSearch)
            .filter(SavedSearch.user_id == user_id)
            .order_by(SavedSearch.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def count_user_searches(self, db: AsyncSession, user_id: int) -> int:
        """
        Count total saved searches for a user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            int: Total count
        """
        from sqlalchemy import func
        result = await db.execute(
            select(func.count()).select_from(SavedSearch).filter(SavedSearch.user_id == user_id)
        )
        return result.scalar()

    async def update(
        self, db: AsyncSession, search_id: int, user_id: int, update_data: dict
    ) -> SavedSearch | None:
        """
        Update a saved search

        Args:
            db: Database session
            search_id: Search ID
            user_id: User ID (for authorization)
            update_data: Data to update

        Returns:
            Optional[SavedSearch]: Updated saved search or None
        """
        saved_search = await self.get_by_id(db, search_id, user_id)
        if not saved_search:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(saved_search, key):
                setattr(saved_search, key, value)

        await db.commit()
        await db.refresh(saved_search)
        return saved_search

    async def delete(self, db: AsyncSession, search_id: int, user_id: int) -> bool:
        """
        Delete a saved search

        Args:
            db: Database session
            search_id: Search ID
            user_id: User ID (for authorization)

        Returns:
            bool: True if deleted, False if not found
        """
        saved_search = await self.get_by_id(db, search_id, user_id)
        if not saved_search:
            return False

        await db.delete(saved_search)
        await db.commit()
        return True

    async def update_new_matches_count(
        self, db: AsyncSession, search_id: int, count: int
    ) -> SavedSearch | None:
        """
        Update the new matches count for a saved search

        Args:
            db: Database session
            search_id: Search ID
            count: New matches count

        Returns:
            Optional[SavedSearch]: Updated saved search or None
        """
        result = await db.execute(select(SavedSearch).filter(SavedSearch.id == search_id))
        saved_search = result.scalar_one_or_none()
        if not saved_search:
            return None

        saved_search.new_matches_count = count
        from datetime import datetime

        saved_search.last_checked = datetime.utcnow()

        await db.commit()
        await db.refresh(saved_search)
        return saved_search


# Singleton instance
saved_search_repository = SavedSearchRepository()
