"""
Pydantic schemas for request/response validation
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.utils.validators import (
    validate_mileage,
    validate_price,
    validate_vin,
    validate_year,
)


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
    vehicle_vin: str = Field(..., min_length=17, max_length=17, description="17-character VIN")
    asking_price: float = Field(..., gt=0)
    offer_price: float | None = Field(None, gt=0)
    status: DealStatus = DealStatus.PENDING
    notes: str | None = Field(None, max_length=5000)

    @field_validator("vehicle_vin")
    @classmethod
    def validate_vin_format(cls, v: str) -> str:
        """Validate VIN format"""
        return validate_vin(v)

    @field_validator("vehicle_year")
    @classmethod
    def validate_year_range(cls, v: int) -> int:
        """Validate vehicle year"""
        return validate_year(v)

    @field_validator("vehicle_mileage")
    @classmethod
    def validate_mileage_range(cls, v: int) -> int:
        """Validate vehicle mileage"""
        return validate_mileage(v)

    @field_validator("asking_price", "offer_price")
    @classmethod
    def validate_price_range(cls, v: float | None) -> float | None:
        """Validate price"""
        if v is not None:
            return validate_price(v)
        return v

    @field_validator("customer_name", "vehicle_make", "vehicle_model")
    @classmethod
    def sanitize_text_fields(cls, v: str) -> str:
        """Sanitize text fields"""
        return v.strip() if v else v


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
    vehicle_vin: str | None = Field(
        None, min_length=17, max_length=17, description="17-character VIN"
    )
    asking_price: float | None = Field(None, gt=0)
    offer_price: float | None = Field(None, gt=0)
    status: DealStatus | None = None
    notes: str | None = Field(None, max_length=5000)

    @field_validator("vehicle_vin")
    @classmethod
    def validate_vin_format(cls, v: str | None) -> str | None:
        """Validate VIN format"""
        if v is not None:
            return validate_vin(v)
        return v

    @field_validator("vehicle_year")
    @classmethod
    def validate_year_range(cls, v: int | None) -> int | None:
        """Validate vehicle year"""
        if v is not None:
            return validate_year(v)
        return v

    @field_validator("vehicle_mileage")
    @classmethod
    def validate_mileage_range(cls, v: int | None) -> int | None:
        """Validate vehicle mileage"""
        if v is not None:
            return validate_mileage(v)
        return v

    @field_validator("asking_price", "offer_price")
    @classmethod
    def validate_price_range(cls, v: float | None) -> float | None:
        """Validate price"""
        if v is not None:
            return validate_price(v)
        return v


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

    @field_validator("username")
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        """Validate username format"""
        from app.utils.validators import validate_username

        return validate_username(v)


class UserCreate(UserBase):
    """Schema for creating a user"""

    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength"""
        from app.utils.validators import validate_password_strength

        return validate_password_strength(v)


class UserUpdate(BaseModel):
    """Schema for updating a user"""

    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=100)
    full_name: str | None = Field(None, max_length=255)
    password: str | None = Field(None, min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def validate_username_format(cls, v: str | None) -> str | None:
        """Validate username format"""
        if v is not None:
            from app.utils.validators import validate_username

            return validate_username(v)
        return v

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str | None) -> str | None:
        """Validate password strength"""
        if v is not None:
            from app.utils.validators import validate_password_strength

            return validate_password_strength(v)
        return v


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
        ...,
        min_length=1,
        max_length=50,
        description="Vehicle condition (e.g., excellent, good)",
    )
    mileage: int = Field(..., ge=0, description="Current mileage in miles")
    make: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Vehicle make (optional but recommended for MarketCheck data)",
    )
    model: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Vehicle model (optional but recommended for MarketCheck data)",
    )
    year: int | None = Field(
        None,
        ge=1900,
        le=2100,
        description="Vehicle year (optional but recommended for MarketCheck data)",
    )
    zip_code: str | None = Field(
        None,
        min_length=5,
        max_length=10,
        description="ZIP code for location-based pricing (optional)",
    )


class DealEvaluationResponse(BaseModel):
    """Schema for deal evaluation response"""

    fair_value: float = Field(..., description="Estimated fair market value in USD")
    score: float = Field(..., ge=1, le=10, description="Deal quality score (1-10)")
    insights: list[str] = Field(default_factory=list, description="AI-powered insights")
    talking_points: list[str] = Field(
        default_factory=list, description="Negotiation talking points"
    )
    market_data: dict | None = Field(
        None, description="MarketCheck market data (comparables_found, summary, comparables)"
    )


class FavoriteBase(BaseModel):
    """Base favorite schema"""

    vin: str = Field(..., min_length=17, max_length=17, description="17-character VIN")
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

    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True
