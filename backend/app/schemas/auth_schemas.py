"""
Authentication-related Pydantic schemas
"""

from pydantic import BaseModel, EmailStr, Field


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
    password: str = Field(..., min_length=8)


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema"""

    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    """Forgot password request schema"""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request schema"""

    token: str
    new_password: str = Field(..., min_length=8)


class ForgotPasswordResponse(BaseModel):
    """Forgot password response schema"""

    message: str
