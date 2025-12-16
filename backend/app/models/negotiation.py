"""
SQLAlchemy models for Negotiation feature
"""

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.sql import func

from app.db.session import Base


class NegotiationStatus(str, enum.Enum):
    """Negotiation session status enumeration"""

    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class MessageRole(str, enum.Enum):
    """Message role enumeration"""

    USER = "user"
    AGENT = "agent"
    DEALER_SIM = "dealer_sim"


class NegotiationSession(Base):
    """Negotiation session model"""

    __tablename__ = "negotiation_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    deal_id = Column(Integer, ForeignKey("deals.id"), nullable=False, index=True)
    status = Column(
        Enum(NegotiationStatus), default=NegotiationStatus.ACTIVE, nullable=False, index=True
    )
    current_round = Column(Integer, default=1, nullable=False)
    max_rounds = Column(Integer, default=10, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<NegotiationSession {self.id}: User {self.user_id}, Deal {self.deal_id}>"


class NegotiationMessage(Base):
    """Negotiation message model"""

    __tablename__ = "negotiation_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(
        Integer, ForeignKey("negotiation_sessions.id"), nullable=False, index=True
    )
    role = Column(Enum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    round_number = Column(Integer, nullable=False, index=True)
    metadata = Column(JSON, nullable=True)  # For agent reasoning, pricing details, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return (
            f"<NegotiationMessage {self.id}: "
            f"Session {self.session_id}, Round {self.round_number}, Role {self.role}>"
        )
