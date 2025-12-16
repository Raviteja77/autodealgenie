"""
SQLAlchemy models for Deal Evaluation
"""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String
from sqlalchemy.sql import func

from app.db.session import Base


class EvaluationStatus(str, enum.Enum):
    """Evaluation status enumeration"""

    ANALYZING = "analyzing"
    AWAITING_INPUT = "awaiting_input"
    COMPLETED = "completed"


class PipelineStep(str, enum.Enum):
    """Pipeline step enumeration"""

    VEHICLE_CONDITION = "vehicle_condition"
    PRICE = "price"
    FINANCING = "financing"
    RISK = "risk"
    FINAL = "final"


class DealEvaluation(Base):
    """Deal Evaluation model"""

    __tablename__ = "deal_evaluations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, index=True)
    status = Column(
        Enum(EvaluationStatus), default=EvaluationStatus.ANALYZING, nullable=False, index=True
    )
    current_step = Column(
        Enum(PipelineStep), default=PipelineStep.VEHICLE_CONDITION, nullable=False
    )
    result_json = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<DealEvaluation {self.id}: Deal {self.deal_id} - {self.status}>"
