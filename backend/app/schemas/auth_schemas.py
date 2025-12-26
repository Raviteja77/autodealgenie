"""
Authentication-related Pydantic schemas
"""

from app.utils.validators import validate_password_strength
from pydantic import BaseModel, EmailStr, Field, field_validator


class Token(BaseModel):
    """Token response schema"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload schema"""

    sub: int  # User ID
    exp: int  # Expiration timestamp
    type: str  # Token type (access or refresh)


class LoginRequest(BaseModel):
    """Login request schema"""

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase"""
        return v.lower().strip()

    @field_validator("password")
    @classmethod
    def check_password_strength(cls, v: str) -> str:
        """Validate password strength"""

        return validate_password_strength(v)


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""

    refresh_token: str = Field(..., min_length=10)


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""

    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Normalize email to lowercase"""
        return v.lower().strip()


class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""

    token: str = Field(..., min_length=10)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength"""
        from app.utils.validators import validate_password_strength

        return validate_password_strength(v)


class ForgotPasswordResponse(BaseModel):
    """Forgot password response schema"""

    message: str
