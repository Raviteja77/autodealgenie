from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.models.vehicle_cache import VehicleCache

class VehicleCacheRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_or_update(self, vehicle_id: str, data: dict) -> VehicleCache:
        """Add or update a vehicle cache entry"""
        pass

    async def get(self, vehicle_id: str) -> Optional[VehicleCache]:
        """Retrieve a vehicle cache entry by ID"""
        pass

    async def remove(self, vehicle_id: str) -> None:
        """Delete a vehicle cache entry"""
        pass