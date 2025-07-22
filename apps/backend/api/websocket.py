"""
WebSocket API routes
Re-exports WebSocket functionality for clean imports
"""
from core.websocket import websocket_endpoint, manager

# Re-export for use in main.py
__all__ = ["websocket_endpoint", "manager"]