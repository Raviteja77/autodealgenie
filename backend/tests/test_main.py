"""Test main API endpoints"""
import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.main import request_id_middleware


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_request_id_middleware_headers_and_state():
    """
    Test that the middleware:
    1. Generates a request ID and adds it to request.state
    2. Adds X-Request-ID header to response
    3. Adds X-Process-Time header to response
    """
    # Create a dedicated app for testing to isolate the middleware
    app = FastAPI()
    app.middleware("http")(request_id_middleware)

    @app.get("/test-middleware")
    async def test_endpoint(request: Request):
        return {"request_id": getattr(request.state, "request_id", None)}

    client = TestClient(app)
    response = client.get("/test-middleware")

    # Verify successful response
    assert response.status_code == 200

    # Verify X-Request-ID header
    assert "X-Request-ID" in response.headers
    request_id = response.headers["X-Request-ID"]
    assert len(request_id) > 0

    # Verify request_id in state matches header
    assert response.json()["request_id"] == request_id

    # Verify X-Process-Time header
    assert "X-Process-Time" in response.headers
    try:
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0
    except ValueError:
        pytest.fail("X-Process-Time header is not a valid float")

def test_request_id_middleware_flow():
    """
    Test that the middleware doesn't break normal request/response flow
    """
    app = FastAPI()
    app.middleware("http")(request_id_middleware)

    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert "X-Request-ID" in response.headers
