"""
Repository for saved search operations in PostgreSQL
"""

from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.models import SavedSearch


class SavedSearchRepository:
    """Repository for managing saved searches"""

    def create(self, db: Session, user_id: int, search_data: dict) -> SavedSearch:
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
        db.commit()
        db.refresh(saved_search)
        return saved_search

    def get_by_id(
        self, db: Session, search_id: int, user_id: int
    ) -> Optional[SavedSearch]:
        """
        Get a saved search by ID

        Args:
            db: Database session
            search_id: Search ID
            user_id: User ID (for authorization)

        Returns:
            Optional[SavedSearch]: Saved search or None
        """
        return (
            db.query(SavedSearch)
            .filter(and_(SavedSearch.id == search_id, SavedSearch.user_id == user_id))
            .first()
        )

    def get_user_searches(
        self, db: Session, user_id: int, skip: int = 0, limit: int = 100
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
        return (
            db.query(SavedSearch)
            .filter(SavedSearch.user_id == user_id)
            .order_by(SavedSearch.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_user_searches(self, db: Session, user_id: int) -> int:
        """
        Count total saved searches for a user

        Args:
            db: Database session
            user_id: User ID

        Returns:
            int: Total count
        """
        return db.query(SavedSearch).filter(SavedSearch.user_id == user_id).count()

    def update(
        self, db: Session, search_id: int, user_id: int, update_data: dict
    ) -> Optional[SavedSearch]:
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
        saved_search = self.get_by_id(db, search_id, user_id)
        if not saved_search:
            return None

        for key, value in update_data.items():
            if value is not None and hasattr(saved_search, key):
                setattr(saved_search, key, value)

        db.commit()
        db.refresh(saved_search)
        return saved_search

    def delete(self, db: Session, search_id: int, user_id: int) -> bool:
        """
        Delete a saved search

        Args:
            db: Database session
            search_id: Search ID
            user_id: User ID (for authorization)

        Returns:
            bool: True if deleted, False if not found
        """
        saved_search = self.get_by_id(db, search_id, user_id)
        if not saved_search:
            return False

        db.delete(saved_search)
        db.commit()
        return True

    def update_new_matches_count(
        self, db: Session, search_id: int, count: int
    ) -> Optional[SavedSearch]:
        """
        Update the new matches count for a saved search

        Args:
            db: Database session
            search_id: Search ID
            count: New matches count

        Returns:
            Optional[SavedSearch]: Updated saved search or None
        """
        saved_search = db.query(SavedSearch).filter(SavedSearch.id == search_id).first()
        if not saved_search:
            return None

        saved_search.new_matches_count = count
        from datetime import datetime

        saved_search.last_checked = datetime.utcnow()

        db.commit()
        db.refresh(saved_search)
        return saved_search


# Singleton instance
saved_search_repository = SavedSearchRepository()
