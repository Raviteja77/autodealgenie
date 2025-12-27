"""
In-memory queue implementation
Used as a fallback when RabbitMQ is not available (e.g., GCP Free Tier)
"""

import asyncio
import logging
from collections import defaultdict
from typing import Any, Callable

logger = logging.getLogger(__name__)


class InMemoryQueue:
    """In-memory queue with basic pub/sub functionality"""

    def __init__(self):
        """Initialize in-memory queue"""
        self.queues: dict[str, asyncio.Queue] = defaultdict(lambda: asyncio.Queue())
        self.consumers: dict[str, list[Callable]] = defaultdict(list)
        self.running = False
        logger.info("Initialized in-memory queue")

    async def connect(self) -> None:
        """Connect to queue - no-op for in-memory"""
        self.running = True
        logger.info("In-memory queue connected")

    async def close(self) -> None:
        """Close connection - no-op for in-memory"""
        self.running = False
        logger.info("In-memory queue closed")

    async def declare_queue(self, queue_name: str, durable: bool = True) -> None:
        """
        Declare a queue

        Args:
            queue_name: Name of the queue
            durable: Ignored for in-memory queue
        """
        if queue_name not in self.queues:
            self.queues[queue_name] = asyncio.Queue()
            logger.info(f"Declared in-memory queue: {queue_name}")

    async def publish(
        self, queue_name: str, message: dict[str, Any], routing_key: str = ""
    ) -> None:
        """
        Publish message to queue

        Args:
            queue_name: Name of the queue
            message: Message to publish
            routing_key: Ignored for in-memory queue
        """
        await self.declare_queue(queue_name)
        await self.queues[queue_name].put(message)
        logger.debug(f"Published message to queue: {queue_name}")

        # Notify consumers
        for callback in self.consumers.get(queue_name, []):
            try:
                await callback(message)
            except Exception as e:
                logger.error(f"Error in consumer callback: {str(e)}")

    async def consume(
        self, queue_name: str, callback: Callable[[dict[str, Any]], None]
    ) -> None:
        """
        Consume messages from queue

        Args:
            queue_name: Name of the queue
            callback: Async function to call with each message
        """
        await self.declare_queue(queue_name)
        self.consumers[queue_name].append(callback)
        logger.info(f"Registered consumer for queue: {queue_name}")

        # Start consuming existing messages
        while self.running:
            try:
                message = await asyncio.wait_for(
                    self.queues[queue_name].get(), timeout=1.0
                )
                await callback(message)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error consuming message: {str(e)}")

    async def get_channel(self) -> "InMemoryQueue":
        """Get channel - returns self for compatibility"""
        return self

    def is_connected(self) -> bool:
        """Check if queue is connected"""
        return self.running

    async def ping(self) -> bool:
        """Health check"""
        return self.running


# Global in-memory queue instance
in_memory_queue = InMemoryQueue()
