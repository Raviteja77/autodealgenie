"""
Repository pattern for Deal operations
"""

from sqlalchemy.orm import Session

from app.models.models import Deal, DealStatus
from app.schemas.schemas import DealCreate, DealUpdate

NORMALIZE_STATUS = {
    DealStatus.IN_PROGRESS: "in_progress",
    DealStatus.PENDING: "PENDING",
    DealStatus.COMPLETED: "COMPLETED",
    DealStatus.CANCELLED: "CANCELLED",
}


class DealRepository:
    """Repository for Deal database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, deal_in: DealCreate) -> Deal:
        """Create a new deal"""
        # Use mode='json' to properly serialize enums to their string values
        deal = Deal(**deal_in.model_dump(mode="json"))
        if isinstance(deal_in.status, str):
            deal_in.status = NORMALIZE_STATUS.get(deal_in.status, DealStatus.IN_PROGRESS)
        self.db.add(deal)
        self.db.commit()
        self.db.refresh(deal)
        return deal

    def get(self, deal_id: int) -> Deal | None:
        """Get a deal by ID"""
        return self.db.query(Deal).filter(Deal.id == deal_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Deal]:
        """Get all deals with pagination"""
        return self.db.query(Deal).offset(skip).limit(limit).all()

    def get_by_status(self, status: str, skip: int = 0, limit: int = 100) -> list[Deal]:
        """Get deals by status"""
        return self.db.query(Deal).filter(Deal.status == status).offset(skip).limit(limit).all()

    def get_by_email(self, email: str) -> list[Deal]:
        """Get deals by customer email"""
        return self.db.query(Deal).filter(Deal.customer_email == email).all()

    def get_deal_by_vehicle_and_customer(
        self, vehicle_vin: str, customer_email: str
    ) -> Deal | None:
        """
        Get a deal by vehicle VIN and customer email.
        """
        return (
            self.db.query(Deal)
            .filter(Deal.vehicle_vin == vehicle_vin, Deal.customer_email == customer_email)
            .first()
        )

    def update(self, deal_id: int, deal_in: DealUpdate) -> Deal | None:
        """Update a deal"""
        deal = self.get(deal_id)
        if not deal:
            return None

        # Use mode='json' to properly serialize enums
        update_data = deal_in.model_dump(exclude_unset=True, mode="json")
        for field, value in update_data.items():
            setattr(deal, field, value)

        self.db.commit()
        self.db.refresh(deal)
        return deal

    def delete(self, deal_id: int) -> bool:
        """Delete a deal"""
        deal = self.get(deal_id)
        if not deal:
            return False

        self.db.delete(deal)
        self.db.commit()
        return True
