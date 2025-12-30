"""
Repository pattern for Favorite operations
"""

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Favorite
from app.schemas.schemas import FavoriteCreate


class FavoriteRepository:
    """Repository for Favorite database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, user_id: int, favorite_in: FavoriteCreate) -> Favorite:
        """Create a new favorite for a user"""
        favorite = Favorite(user_id=user_id, **favorite_in.model_dump())
        self.db.add(favorite)
        await self.db.commit()
        await self.db.refresh(favorite)
        return favorite

    async def get_by_id(self, favorite_id: int) -> Favorite | None:
        """Get a favorite by ID"""
        result = await self.db.execute(select(Favorite).filter(Favorite.id == favorite_id))
        return result.scalar_one_or_none()

    async def get_by_user_and_vin(self, user_id: int, vin: str) -> Favorite | None:
        """Get a specific favorite by user ID and VIN"""
        result = await self.db.execute(
            select(Favorite).filter(Favorite.user_id == user_id, Favorite.vin == vin)
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> list[Favorite]:
        """Get all favorites for a user with pagination"""
        result = await self.db.execute(
            select(Favorite)
            .filter(Favorite.user_id == user_id)
            .order_by(desc(Favorite.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def delete(self, favorite_id: int) -> bool:
        """Delete a favorite by ID"""
        favorite = await self.get_by_id(favorite_id)
        if not favorite:
            return False

        await self.db.delete(favorite)
        await self.db.commit()
        return True

    async def delete_by_user_and_vin(self, user_id: int, vin: str) -> bool:
        """Delete a favorite by user ID and VIN"""
        favorite = await self.get_by_user_and_vin(user_id, vin)
        if not favorite:
            return False

        await self.db.delete(favorite)
        await self.db.commit()
        return True

    async def exists(self, user_id: int, vin: str) -> bool:
        """Check if a favorite exists for a user and VIN"""
        result = await self.get_by_user_and_vin(user_id, vin)
        return result is not None
