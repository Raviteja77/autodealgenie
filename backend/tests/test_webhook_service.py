"""
Tests for webhook service
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.models.models import WebhookStatus, WebhookSubscription
from app.services.webhook_service import WebhookService


@pytest.mark.asyncio
async def test_send_webhook_success():
    """Test successful webhook delivery"""
    service = WebhookService(timeout=10)

    subscription = WebhookSubscription(
        id=1,
        user_id=1,
        webhook_url="https://example.com/webhook",
        status=WebhookStatus.ACTIVE,
        make="Toyota",
    )

    vehicle_data = {
        "vin": "123ABC",
        "make": "Toyota",
        "model": "RAV4",
        "price": 25000,
        "year": 2022,
    }

    # Mock httpx client
    mock_response = AsyncMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient", return_value=mock_client):
        success, message = await service.send_webhook(subscription, vehicle_data)

        assert success is True
        assert message == "Success"
        mock_client.post.assert_called_once()


@pytest.mark.asyncio
async def test_send_webhook_failure_http_error():
    """Test webhook delivery with HTTP error"""
    service = WebhookService(timeout=10)

    subscription = WebhookSubscription(
        id=1,
        user_id=1,
        webhook_url="https://example.com/webhook",
        status=WebhookStatus.ACTIVE,
    )

    vehicle_data = {"vin": "123ABC", "make": "Toyota"}

    # Mock httpx client with error response
    mock_response = AsyncMock()
    mock_response.status_code = 500

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient", return_value=mock_client):
        success, message = await service.send_webhook(subscription, vehicle_data)

        assert success is False
        assert "HTTP 500" in message


@pytest.mark.asyncio
async def test_send_webhook_timeout():
    """Test webhook delivery timeout"""
    service = WebhookService(timeout=1)

    subscription = WebhookSubscription(
        id=1,
        user_id=1,
        webhook_url="https://example.com/webhook",
        status=WebhookStatus.ACTIVE,
    )

    vehicle_data = {"vin": "123ABC", "make": "Toyota"}

    # Mock httpx client with timeout exception
    from httpx import TimeoutException

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=False)  # Allow exceptions to propagate
    mock_client.post = AsyncMock(side_effect=TimeoutException("Timeout"))

    with patch("httpx.AsyncClient", return_value=mock_client):
        success, message = await service.send_webhook(subscription, vehicle_data)

        assert success is False
        assert message == "Timeout"


@pytest.mark.asyncio
async def test_send_webhook_with_secret_token():
    """Test webhook delivery with secret token"""
    service = WebhookService(timeout=10)

    subscription = WebhookSubscription(
        id=1,
        user_id=1,
        webhook_url="https://example.com/webhook",
        status=WebhookStatus.ACTIVE,
        secret_token="my-secret-token",
    )

    vehicle_data = {"vin": "123ABC", "make": "Toyota"}

    # Mock httpx client
    mock_response = AsyncMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient", return_value=mock_client):
        success, message = await service.send_webhook(subscription, vehicle_data)

        assert success is True

        # Verify secret token was included in headers
        call_args = mock_client.post.call_args
        headers = call_args.kwargs["headers"]
        assert headers["X-Webhook-Secret"] == "my-secret-token"


@pytest.mark.asyncio
async def test_send_vehicle_alerts_multiple_subscriptions():
    """Test sending alerts to multiple subscriptions"""
    service = WebhookService(timeout=10)

    subscriptions = [
        WebhookSubscription(
            id=1,
            user_id=1,
            webhook_url="https://example.com/webhook1",
            status=WebhookStatus.ACTIVE,
        ),
        WebhookSubscription(
            id=2,
            user_id=2,
            webhook_url="https://example.com/webhook2",
            status=WebhookStatus.ACTIVE,
        ),
        WebhookSubscription(
            id=3,
            user_id=3,
            webhook_url="https://example.com/webhook3",
            status=WebhookStatus.ACTIVE,
        ),
    ]

    vehicle_data = {"vin": "123ABC", "make": "Toyota"}

    # Mock successful webhook sends
    mock_response = AsyncMock()
    mock_response.status_code = 200

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await service.send_vehicle_alerts(subscriptions, vehicle_data)

        assert result["total"] == 3
        assert result["success"] == 3
        assert result["failed"] == 0


@pytest.mark.asyncio
async def test_send_vehicle_alerts_mixed_results():
    """Test sending alerts with some successes and some failures"""
    service = WebhookService(timeout=10)

    subscriptions = [
        WebhookSubscription(
            id=1,
            user_id=1,
            webhook_url="https://example.com/webhook1",
            status=WebhookStatus.ACTIVE,
        ),
        WebhookSubscription(
            id=2,
            user_id=2,
            webhook_url="https://example.com/webhook2",
            status=WebhookStatus.ACTIVE,
        ),
    ]

    vehicle_data = {"vin": "123ABC", "make": "Toyota"}

    # Mock one success, one failure
    mock_response_success = AsyncMock()
    mock_response_success.status_code = 200

    mock_response_failure = AsyncMock()
    mock_response_failure.status_code = 500

    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock()
    mock_client.post = AsyncMock(side_effect=[mock_response_success, mock_response_failure])

    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await service.send_vehicle_alerts(subscriptions, vehicle_data)

        assert result["total"] == 2
        assert result["success"] == 1
        assert result["failed"] == 1


@pytest.mark.asyncio
async def test_send_vehicle_alerts_empty_list():
    """Test sending alerts with empty subscription list"""
    service = WebhookService(timeout=10)

    vehicle_data = {"vin": "123ABC", "make": "Toyota"}

    result = await service.send_vehicle_alerts([], vehicle_data)

    assert result["total"] == 0
    assert result["success"] == 0
    assert result["failed"] == 0
