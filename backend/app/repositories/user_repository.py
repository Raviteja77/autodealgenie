"""
User repository for database operations
"""

import secrets
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.models import User
from app.schemas.schemas import UserCreate


class UserRepository:
    """Repository for user database operations"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_by_username(self, username: str) -> User | None:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create(self, user_in: UserCreate) -> User:
        """Create a new user"""
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def authenticate(self, email: str, password: str) -> User | None:
        """Authenticate a user by email and password"""
        user = self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    def create_password_reset_token(self, email: str) -> str | None:
        """Create a password reset token for a user"""
        user = self.get_by_email(email)
        if not user:
            return None

        # Generate a secure random token
        token = secrets.token_urlsafe(32)

        # Set token expiration to 1 hour from now
        user.reset_token = token
        user.reset_token_expires = datetime.now(timezone.utc) + timedelta(hours=1)

        self.db.commit()
        return token

    def verify_reset_token(self, token: str) -> User | None:
        """Verify a password reset token and return the user if valid"""
        user = self.db.query(User).filter(User.reset_token == token).first()

        if not user:
            return None

        # Check if token has expired
        if not user.reset_token_expires or user.reset_token_expires < datetime.now(
            timezone.utc
        ):
            return None

        return user

    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset a user's password using a valid token"""
        user = self.verify_reset_token(token)

        if not user:
            return False

        # Update password and clear reset token
        user.hashed_password = get_password_hash(new_password)
        user.reset_token = None
        user.reset_token_expires = None

        self.db.commit()
        return True

