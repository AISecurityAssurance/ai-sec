"""
WebSocket Manager for Real-time Updates
Handles WebSocket connections and broadcasts analysis progress
"""
from typing import Dict, List, Set, Optional, Any
import json
import asyncio
from datetime import datetime
from uuid import UUID
import logging

from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from core.models.schemas import AnalysisStatus

logger = logging.getLogger(__name__)


class WSMessage(BaseModel):
    """WebSocket message format"""
    type: str  # connection, analysis_update, section_update, error, notification
    timestamp: datetime
    data: Dict[str, Any]
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps({
            "type": self.type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        })


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting"""
    
    def __init__(self):
        # Active connections by user ID
        self.active_connections: Dict[str, List[WebSocket]] = {}
        # Analysis subscriptions: analysis_id -> set of user_ids
        self.analysis_subscriptions: Dict[str, Set[str]] = {}
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, user_id: str, metadata: Optional[Dict[str, Any]] = None):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        
        # Add to active connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        
        # Store metadata
        self.connection_metadata[websocket] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            **(metadata or {})
        }
        
        # Send connection confirmation
        await self._send_personal_message(
            WSMessage(
                type="connection",
                timestamp=datetime.utcnow(),
                data={
                    "status": "connected",
                    "user_id": user_id,
                    "message": "WebSocket connection established"
                }
            ),
            websocket
        )
        
        logger.info(f"User {user_id} connected via WebSocket")
        
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        metadata = self.connection_metadata.get(websocket, {})
        user_id = metadata.get("user_id")
        
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
                
        # Clean up subscriptions
        for analysis_id, subscribers in list(self.analysis_subscriptions.items()):
            if user_id in subscribers:
                subscribers.remove(user_id)
                if not subscribers:
                    del self.analysis_subscriptions[analysis_id]
                    
        # Remove metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
            
        logger.info(f"User {user_id} disconnected from WebSocket")
        
    async def subscribe_to_analysis(self, user_id: str, analysis_id: str):
        """Subscribe a user to analysis updates"""
        if analysis_id not in self.analysis_subscriptions:
            self.analysis_subscriptions[analysis_id] = set()
        self.analysis_subscriptions[analysis_id].add(user_id)
        
        # Notify user of subscription
        await self.send_personal_message(
            user_id,
            WSMessage(
                type="notification",
                timestamp=datetime.utcnow(),
                data={
                    "message": f"Subscribed to analysis {analysis_id}",
                    "analysis_id": analysis_id
                }
            )
        )
        
    async def unsubscribe_from_analysis(self, user_id: str, analysis_id: str):
        """Unsubscribe a user from analysis updates"""
        if analysis_id in self.analysis_subscriptions:
            self.analysis_subscriptions[analysis_id].discard(user_id)
            if not self.analysis_subscriptions[analysis_id]:
                del self.analysis_subscriptions[analysis_id]
                
    async def broadcast_analysis_update(
        self,
        analysis_id: str,
        status: AnalysisStatus,
        progress: float,
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Broadcast analysis status update to all subscribers"""
        if analysis_id not in self.analysis_subscriptions:
            return
            
        message_data = WSMessage(
            type="analysis_update",
            timestamp=datetime.utcnow(),
            data={
                "analysis_id": analysis_id,
                "status": status.value,
                "progress": progress,
                "message": message,
                **(metadata or {})
            }
        )
        
        # Send to all subscribers
        for user_id in self.analysis_subscriptions[analysis_id]:
            await self.send_personal_message(user_id, message_data)
            
    async def broadcast_section_update(
        self,
        analysis_id: str,
        framework: str,
        section_id: str,
        status: str,
        content: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """Broadcast section update to all subscribers"""
        if analysis_id not in self.analysis_subscriptions:
            return
            
        message_data = WSMessage(
            type="section_update",
            timestamp=datetime.utcnow(),
            data={
                "analysis_id": analysis_id,
                "framework": framework,
                "section_id": section_id,
                "status": status,
                "content": content,
                "error": error
            }
        )
        
        # Send to all subscribers
        for user_id in self.analysis_subscriptions[analysis_id]:
            await self.send_personal_message(user_id, message_data)
            
    async def send_personal_message(self, user_id: str, message: WSMessage):
        """Send a message to all connections of a specific user"""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await self._send_personal_message(message, connection)
                
    async def _send_personal_message(self, message: WSMessage, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message.to_json())
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
            # Connection might be broken, disconnect it
            self.disconnect(websocket)
            
    async def handle_message(self, websocket: WebSocket, data: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        metadata = self.connection_metadata.get(websocket, {})
        user_id = metadata.get("user_id")
        
        if not user_id:
            logger.error("WebSocket message from unknown connection")
            return
            
        message_type = data.get("type")
        
        if message_type == "subscribe":
            analysis_id = data.get("analysis_id")
            if analysis_id:
                await self.subscribe_to_analysis(user_id, analysis_id)
                
        elif message_type == "unsubscribe":
            analysis_id = data.get("analysis_id")
            if analysis_id:
                await self.unsubscribe_from_analysis(user_id, analysis_id)
                
        elif message_type == "ping":
            # Respond with pong
            await self._send_personal_message(
                WSMessage(
                    type="pong",
                    timestamp=datetime.utcnow(),
                    data={"message": "pong"}
                ),
                websocket
            )
            
        else:
            logger.warning(f"Unknown WebSocket message type: {message_type}")
            
    async def broadcast_to_all(self, message: WSMessage):
        """Broadcast a message to all connected users"""
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                await self._send_personal_message(message, connection)
                
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())
        
    def get_user_count(self) -> int:
        """Get number of unique connected users"""
        return len(self.active_connections)
        
    def get_analysis_subscribers(self, analysis_id: str) -> Set[str]:
        """Get set of users subscribed to an analysis"""
        return self.analysis_subscriptions.get(analysis_id, set())


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint handler"""
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive and handle messages
            data = await websocket.receive_json()
            await manager.handle_message(websocket, data)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)