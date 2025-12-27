"""
RabbitMQ producer for publishing messages
"""

import json
import logging
from typing import Any

import aio_pika
from aio_pika import DeliveryMode, Message

from app.core.config import settings
from app.db.rabbitmq import rabbitmq

logger = logging.getLogger(__name__)


class RabbitMQProducerService:
    """RabbitMQ producer service for publishing messages"""

    def __init__(self):
        self.initialized = False

    async def start(self):
        """Initialize RabbitMQ producer"""
        try:
            # Connection is managed by the global rabbitmq instance
            # Just declare the queues we'll be using
            await rabbitmq.declare_queue(settings.RABBITMQ_QUEUE_DEALS, durable=True)
            await rabbitmq.declare_queue(settings.RABBITMQ_QUEUE_NOTIFICATIONS, durable=True)
            self.initialized = True
            logger.info("RabbitMQ producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize RabbitMQ producer: {str(e)}")
            raise

    async def stop(self):
        """Stop RabbitMQ producer"""
        self.initialized = False
        logger.info("RabbitMQ producer stopped")

    async def send_message(
        self,
        queue_name: str,
        message: dict[str, Any],
        priority: int = 0,
        persistent: bool = True,
    ):
        """
        Send message to RabbitMQ queue

        Args:
            queue_name: Queue name
            message: Message payload as dictionary
            priority: Message priority (0-9, higher = more important)
            persistent: Whether message should survive broker restart
        """
        if not self.initialized:
            raise RuntimeError("RabbitMQ producer not initialized")

        try:
            channel = await rabbitmq.get_channel()

            # Serialize message to JSON
            message_body = json.dumps(message).encode("utf-8")

            # Create message with appropriate delivery mode
            delivery_mode = DeliveryMode.PERSISTENT if persistent else DeliveryMode.NOT_PERSISTENT

            aio_message = Message(
                body=message_body,
                delivery_mode=delivery_mode,
                priority=priority,
                content_type="application/json",
            )

            # Publish to queue (using default exchange with routing_key = queue_name)
            await channel.default_exchange.publish(
                aio_message,
                routing_key=queue_name,
            )

            logger.info(f"Message sent to queue {queue_name}: {message}")
        except Exception as e:
            logger.error(f"Failed to send message to {queue_name}: {str(e)}")
            raise

    async def send_deal_event(self, deal_data: dict[str, Any], priority: int = 0):
        """
        Send deal event to deals queue

        Args:
            deal_data: Deal data payload
            priority: Message priority (0-9)
        """
        await self.send_message(
            settings.RABBITMQ_QUEUE_DEALS,
            deal_data,
            priority=priority,
        )

    async def send_notification(self, notification_data: dict[str, Any], priority: int = 5):
        """
        Send notification to notifications queue

        Args:
            notification_data: Notification data payload
            priority: Message priority (0-9, default 5 for normal priority)
        """
        await self.send_message(
            settings.RABBITMQ_QUEUE_NOTIFICATIONS,
            notification_data,
            priority=priority,
        )


rabbitmq_producer = RabbitMQProducerService()
