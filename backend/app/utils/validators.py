"""
Custom validators and validation utilities for enhanced input validation
"""

import re
from typing import Any

from pydantic import field_validator


def validate_vin(vin: str) -> str:
    """
    Validate Vehicle Identification Number (VIN)
    - Must be exactly 17 characters
    - Alphanumeric only (no I, O, Q)
    - Check digit validation
    """
    if not vin:
        raise ValueError("VIN is required")
    
    vin = vin.upper().strip()
    
    if len(vin) != 17:
        raise ValueError("VIN must be exactly 17 characters")
    
    # VINs cannot contain I, O, or Q
    if re.search(r'[IOQ]', vin):
        raise ValueError("VIN cannot contain letters I, O, or Q")
    
    # Must be alphanumeric
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
        raise ValueError("VIN must contain only letters (except I, O, Q) and numbers")
    
    return vin


def validate_email_format(email: str) -> str:
    """
    Enhanced email validation beyond basic format check
    """
    email = email.lower().strip()
    
    # Check for common typos in popular domains
    common_typos = {
        'gmial.com': 'gmail.com',
        'gmai.com': 'gmail.com',
        'yahooo.com': 'yahoo.com',
        'hotmial.com': 'hotmail.com',
    }
    
    for typo, correct in common_typos.items():
        if email.endswith(typo):
            raise ValueError(f"Did you mean {correct}? Email appears to have a typo.")
    
    return email


def validate_price(price: float) -> float:
    """
    Validate price is reasonable for automotive context
    """
    if price <= 0:
        raise ValueError("Price must be greater than 0")
    
    if price < 100:
        raise ValueError("Price seems unreasonably low (minimum $100)")
    
    if price > 10_000_000:
        raise ValueError("Price exceeds maximum allowed value ($10,000,000)")
    
    # Check for reasonable decimal places (max 2)
    if round(price, 2) != price:
        raise ValueError("Price can have at most 2 decimal places")
    
    return price


def validate_year(year: int) -> int:
    """
    Validate vehicle year is reasonable
    """
    from datetime import datetime
    
    current_year = datetime.now().year
    min_year = 1900
    max_year = current_year + 2  # Allow next model year
    
    if year < min_year:
        raise ValueError(f"Vehicle year cannot be before {min_year}")
    
    if year > max_year:
        raise ValueError(f"Vehicle year cannot be after {max_year}")
    
    return year


def validate_mileage(mileage: int) -> int:
    """
    Validate vehicle mileage is reasonable
    """
    if mileage < 0:
        raise ValueError("Mileage cannot be negative")
    
    if mileage > 1_000_000:
        raise ValueError("Mileage exceeds reasonable maximum (1,000,000 miles)")
    
    return mileage


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input to prevent injection attacks
    """
    if not value:
        return value
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Trim whitespace
    value = value.strip()
    
    # Enforce max length
    if len(value) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} characters")
    
    return value


def validate_username(username: str) -> str:
    """
    Validate username format and content
    """
    username = username.strip()
    
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters")
    
    if len(username) > 50:
        raise ValueError("Username cannot exceed 50 characters")
    
    # Must start with letter
    if not username[0].isalpha():
        raise ValueError("Username must start with a letter")
    
    # Can only contain alphanumeric, underscore, hyphen
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
        raise ValueError("Username can only contain letters, numbers, underscores, and hyphens")
    
    # Check for reserved usernames
    reserved = ['admin', 'root', 'system', 'api', 'null', 'undefined']
    if username.lower() in reserved:
        raise ValueError("This username is reserved")
    
    return username


def validate_password_strength(password: str) -> str:
    """
    Validate password meets security requirements
    """
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters")
    
    if len(password) > 128:
        raise ValueError("Password cannot exceed 128 characters")
    
    # Check for at least one uppercase
    if not re.search(r'[A-Z]', password):
        raise ValueError("Password must contain at least one uppercase letter")
    
    # Check for at least one lowercase
    if not re.search(r'[a-z]', password):
        raise ValueError("Password must contain at least one lowercase letter")
    
    # Check for at least one digit
    if not re.search(r'\d', password):
        raise ValueError("Password must contain at least one number")
    
    # Check for at least one special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        raise ValueError("Password must contain at least one special character")
    
    # Check for common passwords
    common_passwords = [
        'password123', 'Password123!', '12345678', 'qwerty123',
        'admin123', 'letmein123', 'welcome123'
    ]
    if password.lower() in [p.lower() for p in common_passwords]:
        raise ValueError("Password is too common. Please choose a stronger password")
    
    return password


def validate_phone_number(phone: str | None) -> str | None:
    """
    Validate and normalize phone number
    """
    if not phone:
        return None
    
    # Remove common separators
    phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if valid format (10-15 digits, optional + prefix)
    if not re.match(r'^\+?\d{10,15}$', phone):
        raise ValueError("Invalid phone number format")
    
    return phone


class ValidationMixin:
    """
    Mixin class to add common validators to Pydantic models
    """
    
    @field_validator('email', mode='before')
    @classmethod
    def validate_email(cls, v: Any) -> Any:
        if isinstance(v, str):
            return validate_email_format(v)
        return v
    
    @field_validator('username', mode='before')
    @classmethod
    def validate_username_field(cls, v: Any) -> Any:
        if isinstance(v, str):
            return validate_username(v)
        return v
    
    @field_validator('password', mode='before')
    @classmethod
    def validate_password(cls, v: Any) -> Any:
        if isinstance(v, str):
            return validate_password_strength(v)
        return v
