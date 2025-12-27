"""
RabbitMQ connection setup with aio-pika
"""

import logging

import aio_pika
from aio_pika import Channel
from aio_pika.abc import AbstractRobustConnection

from app.core.config import settings

logger = logging.getLogger(__name__)


class RabbitMQ:
    """RabbitMQ connection manager"""

    connection: AbstractRobustConnection | None = None
    channel: Channel | None = None

    @classmethod
    async def connect(cls):
        """Connect to RabbitMQ"""
        try:
            cls.connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL,
                timeout=10.0,
            )
            cls.channel = await cls.connection.channel()
            # Set QoS for fair dispatch
            await cls.channel.set_qos(prefetch_count=1)
            logger.info("Successfully connected to RabbitMQ")
            logger.info(f"Using URL: {settings.RABBITMQ_URL.split('@')[-1]}")  # Hide credentials
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
            raise

    @classmethod
    async def close(cls):
        """Close RabbitMQ connection"""
        if cls.channel and not cls.channel.is_closed:
            await cls.channel.close()
            logger.info("RabbitMQ channel closed")
        if cls.connection and not cls.connection.is_closed:
            await cls.connection.close()
            logger.info("RabbitMQ connection closed")

    @classmethod
    async def get_channel(cls) -> Channel:
        """Get channel instance"""
        if cls.channel is None or cls.channel.is_closed:
            raise RuntimeError("RabbitMQ channel is not initialized. Call connect() first.")
        return cls.channel

    @classmethod
    async def declare_queue(cls, queue_name: str, durable: bool = True) -> aio_pika.Queue:
        """
        Declare a queue

        Args:
            queue_name: Name of the queue
            durable: Whether the queue should survive broker restart

        Returns:
            Declared queue
        """
        channel = await cls.get_channel()
        queue = await channel.declare_queue(queue_name, durable=durable)
        logger.info(f"Declared queue: {queue_name}")
        return queue

    @classmethod
    async def declare_exchange(
        cls,
        exchange_name: str,
        exchange_type: aio_pika.ExchangeType = aio_pika.ExchangeType.DIRECT,
        durable: bool = True,
    ) -> aio_pika.Exchange:
        """
        Declare an exchange

        Args:
            exchange_name: Name of the exchange
            exchange_type: Type of exchange (direct, fanout, topic, headers)
            durable: Whether the exchange should survive broker restart

        Returns:
            Declared exchange
        """
        channel = await cls.get_channel()
        exchange = await channel.declare_exchange(
            exchange_name,
            exchange_type,
            durable=durable,
        )
        logger.info(f"Declared exchange: {exchange_name} (type: {exchange_type.value})")
        return exchange


rabbitmq = RabbitMQ()
