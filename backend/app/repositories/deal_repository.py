"""
Repository pattern for Deal operations
"""

from sqlalchemy.orm import Session

from app.models.models import Deal
from app.schemas.schemas import DealCreate, DealUpdate


class DealRepository:
    """Repository for Deal database operations"""

    def __init__(self, db: Session):
        self.db = db

    def create(self, deal_in: DealCreate) -> Deal:
        """Create a new deal"""
        deal = Deal(**deal_in.model_dump())
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

    def update(self, deal_id: int, deal_in: DealUpdate) -> Deal | None:
        """Update a deal"""
        deal = self.get(deal_id)
        if not deal:
            return None

        update_data = deal_in.model_dump(exclude_unset=True)
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
