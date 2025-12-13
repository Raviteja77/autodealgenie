"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum


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
    offer_price: Optional[float] = Field(None, gt=0)
    status: DealStatus = DealStatus.PENDING
    notes: Optional[str] = None


class DealCreate(DealBase):
    """Schema for creating a deal"""
    pass


class DealUpdate(BaseModel):
    """Schema for updating a deal"""
    customer_name: Optional[str] = Field(None, min_length=1, max_length=255)
    customer_email: Optional[EmailStr] = None
    vehicle_make: Optional[str] = Field(None, min_length=1, max_length=100)
    vehicle_model: Optional[str] = Field(None, min_length=1, max_length=100)
    vehicle_year: Optional[int] = Field(None, ge=1900, le=2100)
    vehicle_mileage: Optional[int] = Field(None, ge=0)
    asking_price: Optional[float] = Field(None, gt=0)
    offer_price: Optional[float] = Field(None, gt=0)
    status: Optional[DealStatus] = None
    notes: Optional[str] = None


class DealResponse(DealBase):
    """Schema for deal response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
