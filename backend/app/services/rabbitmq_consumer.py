"""
RabbitMQ consumer for consuming messages
"""

import asyncio
import json
import logging
from collections.abc import Callable
from typing import Any

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from app.core.config import settings
from app.db.rabbitmq import rabbitmq

logger = logging.getLogger(__name__)


class RabbitMQConsumerService:
    """RabbitMQ consumer service for consuming messages"""

    def __init__(self, queue_name: str):
        self.queue_name = queue_name
        self.queue: aio_pika.Queue | None = None
        self.consumer_tag: str | None = None
        self.running = False

    async def start(self):
        """Start RabbitMQ consumer"""
        try:
            # Declare the queue
            self.queue = await rabbitmq.declare_queue(self.queue_name, durable=True)
            logger.info(f"RabbitMQ consumer started for queue: {self.queue_name}")
        except Exception as e:
            logger.error(f"Failed to start consumer for queue {self.queue_name}: {str(e)}")
            raise

    async def stop(self):
        """Stop RabbitMQ consumer"""
        self.running = False
        if self.consumer_tag and self.queue:
            try:
                await self.queue.cancel(self.consumer_tag)
                logger.info(f"Consumer cancelled for queue {self.queue_name}")
            except Exception as e:
                logger.error(f"Error cancelling consumer: {str(e)}")
            finally:
                self.consumer_tag = None
        logger.info("RabbitMQ consumer stopped")

    async def consume_messages(self, callback: Callable[[dict[str, Any]], Any]):
        """
        Consume messages from RabbitMQ queue

        Args:
            callback: Async function to handle each message
        """
        if not self.queue:
            raise RuntimeError("RabbitMQ consumer not started")

        self.running = True

        async def process_message(message: AbstractIncomingMessage):
            """Process a single message"""
            async with message.process():
                try:
                    # Deserialize message
                    body = json.loads(message.body.decode("utf-8"))
                    logger.info(f"Received message from queue {self.queue_name}: {body}")

                    # Call the callback
                    await callback(body)

                    # Message is automatically acknowledged due to async with message.process()
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode message: {str(e)}")
                    # Message will be rejected and not requeued
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    # Message will be rejected and not requeued
                    raise

        try:
            # Start consuming
            self.consumer_tag = await self.queue.consume(process_message)
            logger.info(f"Started consuming from queue {self.queue_name}")

            # Keep running until stopped
            while self.running:
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            logger.info(f"Consumer task cancelled for queue {self.queue_name}")
        except Exception as e:
            logger.error(f"Unexpected error in consumer: {str(e)}")
            raise
        finally:
            await self.stop()


async def handle_deal_message(message: dict[str, Any]):
    """Handle deal message"""
    logger.info(f"Processing deal message: {message}")
    # Add your deal processing logic here
    # For now, just log the message


async def handle_notification_message(message: dict[str, Any]):
    """Handle notification message"""
    logger.info(f"Processing notification message: {message}")
    # Add your notification processing logic here
    # For now, just log the message


# Example consumer instances
deals_consumer = RabbitMQConsumerService(settings.RABBITMQ_QUEUE_DEALS)
notifications_consumer = RabbitMQConsumerService(settings.RABBITMQ_QUEUE_NOTIFICATIONS)
