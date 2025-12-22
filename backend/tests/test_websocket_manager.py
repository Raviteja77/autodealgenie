"""
Unit tests for WebSocket connection manager
"""

import pytest
from unittest.mock import AsyncMock

from app.services.websocket_manager import ConnectionManager


@pytest.fixture
def connection_manager():
    """Create a connection manager instance"""
    return ConnectionManager()


@pytest.fixture
def mock_websocket():
    """Create a mock WebSocket"""
    ws = AsyncMock()
    ws.accept = AsyncMock()
    ws.send_json = AsyncMock()
    return ws


@pytest.mark.asyncio
async def test_connect_websocket(connection_manager, mock_websocket):
    """Test connecting a WebSocket"""
    session_id = 1
    
    await connection_manager.connect(mock_websocket, session_id)
    
    # Verify WebSocket was accepted
    mock_websocket.accept.assert_called_once()
    
    # Verify connection was added to active connections
    assert session_id in connection_manager.active_connections
    assert mock_websocket in connection_manager.active_connections[session_id]
    assert connection_manager.get_connection_count(session_id) == 1


@pytest.mark.asyncio
async def test_connect_multiple_websockets(connection_manager, mock_websocket):
    """Test connecting multiple WebSockets to the same session"""
    session_id = 1
    ws1 = mock_websocket
    ws2 = AsyncMock()
    ws2.accept = AsyncMock()
    
    await connection_manager.connect(ws1, session_id)
    await connection_manager.connect(ws2, session_id)
    
    # Verify both connections are tracked
    assert connection_manager.get_connection_count(session_id) == 2


def test_disconnect_websocket(connection_manager, mock_websocket):
    """Test disconnecting a WebSocket"""
    session_id = 1
    connection_manager.active_connections[session_id] = [mock_websocket]
    
    connection_manager.disconnect(mock_websocket, session_id)
    
    # Verify connection was removed
    assert session_id not in connection_manager.active_connections


def test_disconnect_nonexistent_websocket(connection_manager, mock_websocket):
    """Test disconnecting a WebSocket that doesn't exist"""
    session_id = 1
    
    # Should not raise an error
    connection_manager.disconnect(mock_websocket, session_id)


@pytest.mark.asyncio
async def test_send_message(connection_manager, mock_websocket):
    """Test sending a message to connected clients"""
    session_id = 1
    await connection_manager.connect(mock_websocket, session_id)
    
    message = {"type": "new_message", "content": "Hello"}
    await connection_manager.send_message(session_id, message)
    
    # Verify message was sent
    mock_websocket.send_json.assert_called_once_with(message)


@pytest.mark.asyncio
async def test_send_message_no_connections(connection_manager):
    """Test sending a message when no connections exist"""
    session_id = 999
    message = {"type": "test"}
    
    # Should not raise an error
    await connection_manager.send_message(session_id, message)


@pytest.mark.asyncio
async def test_broadcast_typing_indicator(connection_manager, mock_websocket):
    """Test broadcasting typing indicator"""
    session_id = 1
    await connection_manager.connect(mock_websocket, session_id)
    
    await connection_manager.broadcast_typing_indicator(session_id, True)
    
    # Verify typing indicator was sent
    mock_websocket.send_json.assert_called_once()
    call_args = mock_websocket.send_json.call_args[0][0]
    assert call_args["type"] == "typing_indicator"
    assert call_args["is_typing"] is True


@pytest.mark.asyncio
async def test_broadcast_message(connection_manager, mock_websocket):
    """Test broadcasting a new message"""
    session_id = 1
    await connection_manager.connect(mock_websocket, session_id)
    
    message_data = {"id": 1, "content": "Test message"}
    await connection_manager.broadcast_message(session_id, message_data)
    
    # Verify message was broadcast
    mock_websocket.send_json.assert_called_once()
    call_args = mock_websocket.send_json.call_args[0][0]
    assert call_args["type"] == "new_message"
    assert call_args["message"] == message_data


@pytest.mark.asyncio
async def test_broadcast_error(connection_manager, mock_websocket):
    """Test broadcasting an error"""
    session_id = 1
    await connection_manager.connect(mock_websocket, session_id)
    
    error_msg = "Something went wrong"
    await connection_manager.broadcast_error(session_id, error_msg)
    
    # Verify error was broadcast
    mock_websocket.send_json.assert_called_once()
    call_args = mock_websocket.send_json.call_args[0][0]
    assert call_args["type"] == "error"
    assert call_args["error"] == error_msg


@pytest.mark.asyncio
async def test_send_message_handles_disconnection(connection_manager):
    """Test that disconnected clients are removed when sending fails"""
    from fastapi import WebSocketDisconnect
    
    session_id = 1
    ws1 = AsyncMock()
    ws1.accept = AsyncMock()
    ws1.send_json = AsyncMock(side_effect=WebSocketDisconnect())
    
    ws2 = AsyncMock()
    ws2.accept = AsyncMock()
    ws2.send_json = AsyncMock()
    
    await connection_manager.connect(ws1, session_id)
    await connection_manager.connect(ws2, session_id)
    
    # Send message - ws1 should be removed due to disconnect
    message = {"type": "test"}
    await connection_manager.send_message(session_id, message)
    
    # Verify ws1 was removed and ws2 received the message
    assert connection_manager.get_connection_count(session_id) == 1
    ws2.send_json.assert_called_once_with(message)


def test_get_connection_count(connection_manager, mock_websocket):
    """Test getting connection count"""
    session_id = 1
    
    # No connections initially
    assert connection_manager.get_connection_count(session_id) == 0
    
    # Add connections
    connection_manager.active_connections[session_id] = [mock_websocket, mock_websocket]
    assert connection_manager.get_connection_count(session_id) == 2
    
    # Non-existent session
    assert connection_manager.get_connection_count(999) == 0
