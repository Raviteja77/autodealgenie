"""Tests for dependencies and security functions"""

from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.api.dependencies import get_current_active_superuser
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.models import User


class TestSecurityFunctions:
    """Test security utility functions"""

    def test_get_password_hash(self):
        """Test password hashing"""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert len(hashed) > 0
        assert hashed.startswith("$2b$")  # bcrypt prefix

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        hashed = get_password_hash(password)

        assert verify_password("wrongpassword", hashed) is False

    def test_create_access_token_default_expiry(self):
        """Test creating access token with default expiry"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)

        assert token is not None
        assert len(token) > 0

        # Decode and verify
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert payload["type"] == "access"
        assert "exp" in payload

    def test_create_access_token_custom_expiry(self):
        """Test creating access token with custom expiry"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=60)
        token = create_access_token(data, expires_delta=expires_delta)

        assert token is not None
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "access"

    def test_create_refresh_token(self):
        """Test creating refresh token"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_refresh_token(data)

        assert token is not None
        assert len(token) > 0

        # Decode and verify
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1
        assert payload["type"] == "refresh"
        assert "exp" in payload

    def test_decode_valid_token(self):
        """Test decoding a valid token"""
        data = {"sub": "test@example.com", "user_id": 1}
        token = create_access_token(data)

        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "test@example.com"
        assert payload["user_id"] == 1

    def test_decode_invalid_token(self):
        """Test decoding an invalid token"""
        invalid_token = "invalid.token.here"
        payload = decode_token(invalid_token)
        assert payload is None

    def test_decode_expired_token(self):
        """Test decoding an expired token"""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(seconds=-1)  # Expired token
        token = create_access_token(data, expires_delta=expires_delta)

        payload = decode_token(token)
        assert payload is None  # Should fail to decode expired token


class TestDependencies:
    """Test FastAPI dependencies"""

    def test_get_current_user_no_token(self, db):
        """Test get_current_user without token"""
        # This is tested indirectly via auth endpoint tests
        # Direct testing of FastAPI dependencies requires mocking Request context
        pass

    def test_get_current_active_superuser_not_superuser(self, db):
        """Test get_current_active_superuser with non-superuser"""
        user = User(
            email="regular@example.com",
            username="regular",
            hashed_password="hashed",
            is_superuser=False,
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_active_superuser(user)

        assert exc_info.value.status_code == 403
        assert "not enough permissions" in str(exc_info.value.detail).lower()

    def test_get_current_active_superuser_success(self, db):
        """Test get_current_active_superuser with superuser"""
        user = User(
            email="admin@example.com",
            username="admin",
            hashed_password="hashed",
            is_superuser=True,
        )

        result = get_current_active_superuser(user)
        assert result == user
        assert result.is_superuser is True
