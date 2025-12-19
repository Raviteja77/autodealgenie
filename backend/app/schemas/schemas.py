"""
Pydantic schemas for request/response validation
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class DealStatus(str, Enum):
    """Deal status enumeration"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DealBase(BaseModel):
    """Base deal schema"""

    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: EmailStr
    vehicle_make: str = Field(..., min_length=1, max_length=100)
    vehicle_model: str = Field(..., min_length=1, max_length=100)
    vehicle_year: int = Field(..., ge=1900, le=2100)
    vehicle_mileage: int = Field(default=0, ge=0)
    asking_price: float = Field(..., gt=0)
    offer_price: float | None = Field(None, gt=0)
    status: DealStatus = DealStatus.PENDING
    notes: str | None = None


class DealCreate(DealBase):
    """Schema for creating a deal"""

    pass


class DealUpdate(BaseModel):
    """Schema for updating a deal"""

    customer_name: str | None = Field(None, min_length=1, max_length=255)
    customer_email: EmailStr | None = None
    vehicle_make: str | None = Field(None, min_length=1, max_length=100)
    vehicle_model: str | None = Field(None, min_length=1, max_length=100)
    vehicle_year: int | None = Field(None, ge=1900, le=2100)
    vehicle_mileage: int | None = Field(None, ge=0)
    asking_price: float | None = Field(None, gt=0)
    offer_price: float | None = Field(None, gt=0)
    status: DealStatus | None = None
    notes: str | None = None


class DealResponse(DealBase):
    """Schema for deal response"""

    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base user schema"""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a user"""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=8)


class UserResponse(UserBase):
    """Schema for user response"""

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class HealthCheck(BaseModel):
    """Health check response"""

    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class DealEvaluationRequest(BaseModel):
    """Schema for deal evaluation request"""

    vehicle_vin: str = Field(..., min_length=17, max_length=17, description="17-character VIN")
    asking_price: float = Field(..., gt=0, description="Asking price in USD")
    condition: str = Field(
        ..., min_length=1, max_length=50, description="Vehicle condition (e.g., excellent, good)"
    )
    mileage: int = Field(..., ge=0, description="Current mileage in miles")


class DealEvaluationResponse(BaseModel):
    """Schema for deal evaluation response"""

    fair_value: float = Field(..., description="Estimated fair market value in USD")
    score: float = Field(..., ge=1, le=10, description="Deal quality score (1-10)")
    insights: list[str] = Field(default_factory=list, description="AI-powered insights")
    talking_points: list[str] = Field(
        default_factory=list, description="Negotiation talking points"
    )


class FavoriteBase(BaseModel):
    """Base favorite schema"""

    vin: str = Field(..., min_length=1, max_length=100)
    make: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    price: float = Field(..., gt=0)
    mileage: int = Field(default=0, ge=0)
    fuel_type: str | None = Field(None, max_length=50)
    location: str | None = Field(None, max_length=255)
    color: str | None = Field(None, max_length=50)
    condition: str | None = Field(None, max_length=50)
    image: str | None = Field(None, max_length=512)


class FavoriteCreate(FavoriteBase):
    """Schema for creating a favorite"""

    pass


class FavoriteResponse(FavoriteBase):
    """Schema for favorite response"""

    id: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
