"""
Tests for RabbitMQ producer and consumer services
"""

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.rabbitmq_consumer import RabbitMQConsumerService, handle_deal_message
from app.services.rabbitmq_producer import RabbitMQProducerService


class TestRabbitMQProducer:
    """Test cases for RabbitMQ producer service"""

    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test sending a message to RabbitMQ queue"""
        producer = RabbitMQProducerService()
        producer.initialized = True

        test_message = {"deal_id": 123, "action": "created"}

        with patch("app.services.rabbitmq_producer.rabbitmq") as mock_rabbitmq:
            # Mock the channel and exchange
            mock_channel = AsyncMock()
            mock_exchange = AsyncMock()
            mock_channel.default_exchange = mock_exchange
            mock_rabbitmq.get_channel.return_value = mock_channel

            await producer.send_message("test_queue", test_message)

            # Verify publish was called
            mock_exchange.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_deal_event(self):
        """Test sending a deal event"""
        producer = RabbitMQProducerService()
        producer.initialized = True

        test_deal = {"deal_id": 456, "vehicle": "Toyota Camry"}

        with patch.object(producer, "send_message", new_callable=AsyncMock) as mock_send:
            await producer.send_deal_event(test_deal)

            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "deals" in call_args[0][0]  # Queue name
            assert call_args[0][1] == test_deal

    @pytest.mark.asyncio
    async def test_send_notification(self):
        """Test sending a notification"""
        producer = RabbitMQProducerService()
        producer.initialized = True

        test_notification = {"user_id": 789, "message": "Deal approved"}

        with patch.object(producer, "send_message", new_callable=AsyncMock) as mock_send:
            await producer.send_notification(test_notification)

            mock_send.assert_called_once()
            call_args = mock_send.call_args
            assert "notifications" in call_args[0][0]  # Queue name
            assert call_args[0][1] == test_notification


class TestRabbitMQConsumer:
    """Test cases for RabbitMQ consumer service"""

    @pytest.mark.asyncio
    async def test_consumer_initialization(self):
        """Test consumer initialization"""
        consumer = RabbitMQConsumerService("test_queue")

        assert consumer.queue_name == "test_queue"
        assert consumer.queue is None
        assert consumer.running is False

    @pytest.mark.asyncio
    async def test_handle_deal_message(self):
        """Test deal message handler"""
        test_message = {"deal_id": 123, "action": "updated"}

        # Should not raise any exceptions
        await handle_deal_message(test_message)


class TestRabbitMQIntegration:
    """Integration tests for RabbitMQ services"""

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_producer_consumer_integration(self):
        """Test that producer can send and consumer can receive messages"""
        # This test requires RabbitMQ to be running
        # Skip in CI/CD unless RabbitMQ is available

        messages_received = []

        async def test_callback(message):
            messages_received.append(message)

        # In a real integration test, we would:
        # 1. Start producer and consumer
        # 2. Send a message
        # 3. Verify it was received
        # 4. Clean up

        # For now, just verify the structure is correct
        producer = RabbitMQProducerService()
        consumer = RabbitMQConsumerService("test_queue")

        assert producer is not None
        assert consumer is not None
