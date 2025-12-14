"""
SQLAlchemy models for PostgreSQL
"""

import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, Integer, String, Text
from sqlalchemy.sql import func

from app.db.session import Base


class DealStatus(str, enum.Enum):
    """Deal status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WebhookStatus(str, enum.Enum):
    """Webhook subscription status"""

    ACTIVE = "active"
    INACTIVE = "inactive"
    FAILED = "failed"


class Deal(Base):
    """Deal model"""

    __tablename__ = "deals"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(255), nullable=False)
    customer_email = Column(String(255), nullable=False, index=True)
    vehicle_make = Column(String(100), nullable=False)
    vehicle_model = Column(String(100), nullable=False)
    vehicle_year = Column(Integer, nullable=False)
    vehicle_mileage = Column(Integer, default=0)
    asking_price = Column(Float, nullable=False)
    offer_price = Column(Float, nullable=True)
    status = Column(Enum(DealStatus), default=DealStatus.PENDING, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<Deal {self.id}: {self.vehicle_year} {self.vehicle_make} {self.vehicle_model}>"


class User(Base):
    """User model"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Integer, default=1)
    is_superuser = Column(Integer, default=0)
    reset_token = Column(String(255), nullable=True)
    reset_token_expires = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<User {self.id}: {self.username}>"


class WebhookSubscription(Base):
    """Webhook subscription model for vehicle alerts"""

    __tablename__ = "webhook_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    webhook_url = Column(String(512), nullable=False)
    status = Column(Enum(WebhookStatus), default=WebhookStatus.ACTIVE, nullable=False)
    
    # Search criteria filters
    make = Column(String(100), nullable=True)
    model = Column(String(100), nullable=True)
    price_min = Column(Float, nullable=True)
    price_max = Column(Float, nullable=True)
    year_min = Column(Integer, nullable=True)
    year_max = Column(Integer, nullable=True)
    mileage_max = Column(Integer, nullable=True)
    
    # Metadata
    secret_token = Column(String(255), nullable=True)  # For webhook verification
    last_triggered = Column(DateTime(timezone=True), nullable=True)
    failure_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<WebhookSubscription {self.id}: {self.user_id} -> {self.webhook_url}>"
