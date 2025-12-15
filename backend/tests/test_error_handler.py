"""Tests for error handler utility"""

import pytest

from app.utils.error_handler import ApiError


def test_api_error_basic():
    """Test basic ApiError creation"""
    error = ApiError(status_code=404, message="Not found")

    assert error.status_code == 404
    assert error.message == "Not found"
    assert error.details is None
    assert str(error) == "ApiError(404): Not found"


def test_api_error_with_details():
    """Test ApiError with additional details"""
    details = {"field": "email", "issue": "already exists"}
    error = ApiError(status_code=400, message="Validation error", details=details)

    assert error.status_code == 400
    assert error.message == "Validation error"
    assert error.details == details
    assert "Validation error" in str(error)
    assert "field" in str(error)


def test_api_error_to_dict():
    """Test ApiError to_dict conversion"""
    error = ApiError(status_code=500, message="Server error")
    error_dict = error.to_dict()

    assert error_dict["status_code"] == 500
    assert error_dict["message"] == "Server error"
    assert "details" not in error_dict


def test_api_error_to_dict_with_details():
    """Test ApiError to_dict conversion with details"""
    details = {"traceback": "some error traceback"}
    error = ApiError(status_code=500, message="Server error", details=details)
    error_dict = error.to_dict()

    assert error_dict["status_code"] == 500
    assert error_dict["message"] == "Server error"
    assert error_dict["details"] == details


def test_api_error_repr():
    """Test ApiError __repr__ method"""
    error = ApiError(status_code=403, message="Forbidden", details={"user": "test"})
    repr_str = repr(error)

    assert "ApiError" in repr_str
    assert "403" in repr_str
    assert "Forbidden" in repr_str
    assert "user" in repr_str


def test_api_error_inheritance():
    """Test that ApiError inherits from Exception"""
    error = ApiError(status_code=400, message="Bad request")

    assert isinstance(error, Exception)
    assert isinstance(error, ApiError)


def test_api_error_raise():
    """Test raising ApiError exception"""
    with pytest.raises(ApiError) as exc_info:
        raise ApiError(status_code=401, message="Unauthorized")

    assert exc_info.value.status_code == 401
    assert exc_info.value.message == "Unauthorized"


def test_api_error_various_status_codes():
    """Test ApiError with various HTTP status codes"""
    status_codes = [400, 401, 403, 404, 422, 500, 502, 503]

    for code in status_codes:
        error = ApiError(status_code=code, message=f"Error {code}")
        assert error.status_code == code
        assert str(code) in str(error)


def test_api_error_details_types():
    """Test ApiError with different types of details"""
    # Test with string details
    error1 = ApiError(status_code=400, message="Error", details="Simple string")
    assert error1.details == "Simple string"

    # Test with list details
    error2 = ApiError(status_code=400, message="Error", details=["error1", "error2"])
    assert error2.details == ["error1", "error2"]

    # Test with nested dict details
    error3 = ApiError(
        status_code=400,
        message="Error",
        details={"validation": {"field": "email", "errors": ["required", "invalid"]}},
    )
    assert error3.details["validation"]["field"] == "email"
