"""Tests for error handling middleware"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.middleware.error_middleware import ErrorHandlerMiddleware
from app.utils.error_handler import ApiError


def test_error_middleware_handles_api_error():
    """Test that middleware properly handles ApiError exceptions"""
    # Create a test app with error middleware
    app = FastAPI()
    app.add_middleware(ErrorHandlerMiddleware)

    @app.get("/test-error")
    async def test_error_endpoint():
        raise ApiError(status_code=404, message="Resource not found")

    client = TestClient(app)
    response = client.get("/test-error")

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Resource not found"
    assert data["status_code"] == 404


def test_error_middleware_handles_api_error_with_details():
    """Test that middleware includes details in error response"""
    app = FastAPI()
    app.add_middleware(ErrorHandlerMiddleware)

    @app.get("/test-error-details")
    async def test_error_with_details():
        details = {"field": "email", "reason": "invalid format"}
        raise ApiError(status_code=422, message="Validation failed", details=details)

    client = TestClient(app)
    response = client.get("/test-error-details")

    assert response.status_code == 422
    data = response.json()
    assert data["detail"] == "Validation failed"
    assert data["status_code"] == 422
    assert "details" in data
    assert data["details"]["field"] == "email"
    assert data["details"]["reason"] == "invalid format"


def test_error_middleware_handles_generic_exception():
    """Test that middleware handles unexpected exceptions gracefully"""
    app = FastAPI()
    app.add_middleware(ErrorHandlerMiddleware)

    @app.get("/test-generic-error")
    async def test_generic_error():
        raise ValueError("Something went wrong")

    client = TestClient(app)
    response = client.get("/test-generic-error")

    assert response.status_code == 500
    data = response.json()
    assert data["detail"] == "Internal server error"
    assert data["status_code"] == 500
    # Should not expose internal error details
    assert "ValueError" not in data.get("detail", "")


def test_error_middleware_does_not_affect_normal_requests():
    """Test that middleware doesn't interfere with normal requests"""
    app = FastAPI()
    app.add_middleware(ErrorHandlerMiddleware)

    @app.get("/test-normal")
    async def test_normal_endpoint():
        return {"status": "success", "data": "test"}

    client = TestClient(app)
    response = client.get("/test-normal")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["data"] == "test"


def test_error_middleware_various_status_codes():
    """Test middleware with various HTTP status codes"""
    app = FastAPI()
    app.add_middleware(ErrorHandlerMiddleware)

    @app.get("/test-{status_code}")
    async def test_status_code(status_code: int):
        raise ApiError(status_code=status_code, message=f"Error {status_code}")

    client = TestClient(app)

    # Test various error codes
    for code in [400, 401, 403, 404, 422, 500, 503]:
        response = client.get(f"/test-{code}")
        assert response.status_code == code
        data = response.json()
        assert data["status_code"] == code
        assert str(code) in data["detail"]


def test_error_middleware_no_details():
    """Test that details are not included when None"""
    app = FastAPI()
    app.add_middleware(ErrorHandlerMiddleware)

    @app.get("/test-no-details")
    async def test_no_details():
        raise ApiError(status_code=400, message="Bad request")

    client = TestClient(app)
    response = client.get("/test-no-details")

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Bad request"
    assert data["status_code"] == 400
    # Details key should not be present when details is None
    assert "details" not in data


def test_error_middleware_preserves_response_format():
    """Test that error responses are consistently formatted"""
    app = FastAPI()
    app.add_middleware(ErrorHandlerMiddleware)

    @app.get("/test-format")
    async def test_format():
        raise ApiError(
            status_code=400,
            message="Test error",
            details={"key": "value"},
        )

    client = TestClient(app)
    response = client.get("/test-format")

    data = response.json()
    # Verify response has expected keys
    assert "detail" in data
    assert "status_code" in data
    assert "details" in data
    # Verify data types
    assert isinstance(data["detail"], str)
    assert isinstance(data["status_code"], int)
    assert isinstance(data["details"], dict)
