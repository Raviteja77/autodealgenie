"""
Kafka consumer for consuming messages
"""
from typing import Callable, Dict, Any
from aiokafka import AIOKafkaConsumer
import json
import asyncio

from app.core.config import settings


class KafkaConsumerService:
    """Kafka consumer service for consuming messages"""
    
    def __init__(self, topics: list[str], group_id: str = None):
        self.topics = topics
        self.group_id = group_id or settings.KAFKA_CONSUMER_GROUP
        self.consumer: AIOKafkaConsumer = None
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.running = False
    
    async def start(self):
        """Start Kafka consumer"""
        self.consumer = AIOKafkaConsumer(
            *self.topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest'
        )
        await self.consumer.start()
        print(f"Kafka consumer started for topics: {self.topics}")
    
    async def stop(self):
        """Stop Kafka consumer"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
            print("Kafka consumer stopped")
    
    async def consume_messages(self, callback: Callable[[Dict[str, Any]], None]):
        """
        Consume messages from Kafka topics
        
        Args:
            callback: Function to handle each message
        """
        if not self.consumer:
            raise RuntimeError("Kafka consumer not started")
        
        self.running = True
        try:
            async for message in self.consumer:
                if not self.running:
                    break
                
                print(f"Received message from topic {message.topic}: {message.value}")
                await callback(message.value)
        except asyncio.CancelledError:
            print("Kafka consumer task cancelled")
        finally:
            await self.stop()


async def handle_deal_message(message: Dict[str, Any]):
    """Handle deal message"""
    print(f"Processing deal message: {message}")
    # Add your deal processing logic here


async def handle_notification_message(message: Dict[str, Any]):
    """Handle notification message"""
    print(f"Processing notification message: {message}")
    # Add your notification processing logic here


# Example consumer instances
deals_consumer = KafkaConsumerService([settings.KAFKA_TOPIC_DEALS])
notifications_consumer = KafkaConsumerService([settings.KAFKA_TOPIC_NOTIFICATIONS])
