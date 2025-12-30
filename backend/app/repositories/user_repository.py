"""
User repository for database operations
"""

import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models.models import User
from app.schemas.schemas import UserCreate


class UserRepository:
    """Repository for user database operations"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email"""
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """Get user by username"""
        result = await self.db.execute(select(User).filter(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID"""
        result = self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()

    async def create(self, user_in: UserCreate) -> User:
        """Create a new user"""
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password"""
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    async def create_password_reset_token(self, email: str) -> str | None:
        """Create a password reset token for a user"""
        user = await self.get_by_email(email)
        if not user:
            return None

        # Generate a secure random token using configured length
        token = secrets.token_urlsafe(settings.PASSWORD_RESET_TOKEN_LENGTH)

        # Set token expiration using configured duration
        user.reset_token = token
        user.reset_token_expires = datetime.now(UTC) + timedelta(
            hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS
        )

        await self.db.commit()
        return token

    async def verify_reset_token(self, token: str) -> User | None:
        """Verify a password reset token and return the user if valid"""
        result = await self.db.execute(select(User).filter(User.reset_token == token))
        user = result.scalar_one_or_none()

        if not user:
            return None

        # Check if token has expired
        if not user.reset_token_expires or user.reset_token_expires < datetime.now(UTC):
            return None

        return user

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset a user's password using a valid token"""
        user = await self.verify_reset_token(token)

        if not user:
            return False

        # Update password and clear reset token
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None

        await self.db.commit()
        return True
