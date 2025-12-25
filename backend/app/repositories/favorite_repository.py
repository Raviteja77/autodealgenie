"""
Repository pattern for Favorite operations
"""

from sqlalchemy.orm import Session

from app.models.models import Favorite
from app.schemas.schemas import FavoriteCreate


class FavoriteRepository:
    """Repository for Favorite database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, favorite_in: FavoriteCreate) -> Favorite:
        """Create a new favorite for a user"""
        favorite = Favorite(user_id=user_id, **favorite_in.model_dump())
        self.db.add(favorite)
        self.db.commit()
        self.db.refresh(favorite)
        return favorite

    def get_by_id(self, favorite_id: int) -> Favorite | None:
        """Get a favorite by ID"""
        return self.db.query(Favorite).filter(Favorite.id == favorite_id).first()

    def get_by_user_and_vin(self, user_id: int, vin: str) -> Favorite | None:
        """Get a specific favorite by user ID and VIN"""
        return (
            self.db.query(Favorite).filter(Favorite.user_id == user_id, Favorite.vin == vin).first()
        )

    def get_all_by_user(self, user_id: int, skip: int = 0, limit: int = 100) -> list[Favorite]:
        """Get all favorites for a user with pagination"""
        return (
            self.db.query(Favorite)
            .filter(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def delete(self, favorite_id: int) -> bool:
        """Delete a favorite by ID"""
        favorite = self.get_by_id(favorite_id)
        if not favorite:
            return False

        self.db.delete(favorite)
        self.db.commit()
        return True

    def delete_by_user_and_vin(self, user_id: int, vin: str) -> bool:
        """Delete a favorite by user ID and VIN"""
        favorite = self.get_by_user_and_vin(user_id, vin)
        if not favorite:
            return False

        self.db.delete(favorite)
        self.db.commit()
        return True

    def exists(self, user_id: int, vin: str) -> bool:
        """Check if a favorite exists for a user and VIN"""
        return self.get_by_user_and_vin(user_id, vin) is not None
