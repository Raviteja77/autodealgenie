"""
Webhook service for sending vehicle alert notifications
"""

import asyncio
import logging
from datetime import datetime
from typing import Any

import httpx

from app.models.models import WebhookSubscription

logger = logging.getLogger(__name__)


class WebhookService:
    """Service for sending webhook notifications"""

    def __init__(self, timeout: int = 10, max_concurrent: int = 10):
        """
        Initialize webhook service

        Args:
            timeout: HTTP request timeout in seconds
            max_concurrent: Maximum concurrent webhook requests
        """
        self.timeout = timeout
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def send_webhook(
        self, subscription: WebhookSubscription, vehicle_data: dict[str, Any]
    ) -> tuple[bool, str]:
        """
        Send webhook notification for a vehicle

        Args:
            subscription: Webhook subscription
            vehicle_data: Vehicle data to send

        Returns:
            Tuple of (success: bool, message: str)
        """
        async with self.semaphore:
            payload = {
                "event": "vehicle_alert",
                "timestamp": datetime.utcnow().isoformat(),
                "subscription_id": subscription.id,
                "vehicle": vehicle_data,
                "criteria": {
                    "make": subscription.make,
                    "model": subscription.model,
                    "price_min": subscription.price_min,
                    "price_max": subscription.price_max,
                    "year_min": subscription.year_min,
                    "year_max": subscription.year_max,
                    "mileage_max": subscription.mileage_max,
                },
            }

            headers = {"Content-Type": "application/json"}

            # Add secret token for verification if present
            if subscription.secret_token:
                headers["X-Webhook-Secret"] = subscription.secret_token

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.post(
                        subscription.webhook_url, json=payload, headers=headers
                    )

                    if response.status_code >= 200 and response.status_code < 300:
                        logger.info(
                            f"Webhook sent successfully to {subscription.webhook_url} "
                            f"(subscription_id={subscription.id})"
                        )
                        return True, "Success"
                    else:
                        logger.warning(
                            f"Webhook failed with status {response.status_code} "
                            f"for {subscription.webhook_url} (subscription_id={subscription.id})"
                        )
                        return False, f"HTTP {response.status_code}"

            except httpx.TimeoutException:
                logger.error(
                    f"Webhook timeout for {subscription.webhook_url} "
                    f"(subscription_id={subscription.id})"
                )
                return False, "Timeout"
            except Exception as e:
                logger.error(
                    f"Webhook error for {subscription.webhook_url} "
                    f"(subscription_id={subscription.id}): {str(e)}"
                )
                return False, str(e)

    async def send_vehicle_alerts(
        self, subscriptions: list[WebhookSubscription], vehicle_data: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Send vehicle alerts to multiple subscriptions

        Args:
            subscriptions: List of webhook subscriptions
            vehicle_data: Vehicle data to send

        Returns:
            Dictionary with results summary
        """
        if not subscriptions:
            return {"total": 0, "success": 0, "failed": 0}

        tasks = [self.send_webhook(sub, vehicle_data) for sub in subscriptions]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        success_count = sum(1 for r in results if not isinstance(r, Exception) and r[0])
        failed_count = len(results) - success_count

        logger.info(
            f"Sent {len(subscriptions)} webhooks: {success_count} succeeded, "
            f"{failed_count} failed"
        )

        return {
            "total": len(subscriptions),
            "success": success_count,
            "failed": failed_count,
        }


# Singleton instance
webhook_service = WebhookService()
