"""
Kafka producer for publishing messages
"""

import json
from typing import Any

from aiokafka import AIOKafkaProducer

from app.core.config import settings


class KafkaProducerService:
    """Kafka producer service for publishing messages"""

    def __init__(self):
        self.producer: AIOKafkaProducer = None
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS

    async def start(self):
        """Start Kafka producer"""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        )
        await self.producer.start()
        print(f"Kafka producer started with servers: {self.bootstrap_servers}")

    async def stop(self):
        """Stop Kafka producer"""
        if self.producer:
            await self.producer.stop()
            print("Kafka producer stopped")

    async def send_message(self, topic: str, message: dict[str, Any], key: str = None):
        """
        Send message to Kafka topic

        Args:
            topic: Kafka topic name
            message: Message payload as dictionary
            key: Optional message key
        """
        if not self.producer:
            raise RuntimeError("Kafka producer not started")

        key_bytes = key.encode("utf-8") if key else None
        await self.producer.send_and_wait(topic, message, key=key_bytes)
        print(f"Message sent to topic {topic}: {message}")

    async def send_deal_event(self, deal_data: dict[str, Any]):
        """Send deal event to deals topic"""
        await self.send_message(settings.KAFKA_TOPIC_DEALS, deal_data)

    async def send_notification(self, notification_data: dict[str, Any]):
        """Send notification to notifications topic"""
        await self.send_message(settings.KAFKA_TOPIC_NOTIFICATIONS, notification_data)


kafka_producer = KafkaProducerService()
