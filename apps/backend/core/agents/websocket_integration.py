"""
WebSocket integration for agents
Sends real-time updates during analysis
"""
from typing import Optional, Dict, Any
import asyncio
from uuid import UUID

from core.websocket import manager
from core.models.schemas import AnalysisStatus
from core.agents.types import SectionResult


class AgentWebSocketNotifier:
    """Handles WebSocket notifications for agent operations"""
    
    def __init__(self, analysis_id: str):
        self.analysis_id = analysis_id
        
    async def notify_analysis_start(self, framework: str):
        """Notify that analysis has started"""
        await manager.broadcast_analysis_update(
            self.analysis_id,
            AnalysisStatus.IN_PROGRESS,
            0.0,
            f"Starting {framework} analysis..."
        )
        
    async def notify_analysis_progress(
        self, 
        progress: float, 
        message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Notify analysis progress update"""
        await manager.broadcast_analysis_update(
            self.analysis_id,
            AnalysisStatus.IN_PROGRESS,
            progress,
            message,
            metadata
        )
        
    async def notify_section_start(
        self,
        framework: str,
        section_id: str,
        section_title: str
    ):
        """Notify that a section analysis has started"""
        await manager.broadcast_section_update(
            self.analysis_id,
            framework,
            section_id,
            "in_progress",
            content={"title": section_title}
        )
        
    async def notify_section_complete(
        self,
        framework: str,
        section: SectionResult
    ):
        """Notify that a section analysis has completed"""
        await manager.broadcast_section_update(
            self.analysis_id,
            framework,
            section.section_id,
            section.status.value,
            content=section.content,
            error=section.error
        )
        
    async def notify_analysis_complete(
        self,
        framework: str,
        success: bool = True,
        error: Optional[str] = None
    ):
        """Notify that analysis has completed"""
        status = AnalysisStatus.COMPLETED if success else AnalysisStatus.FAILED
        message = f"{framework} analysis completed" if success else f"{framework} analysis failed: {error}"
        
        await manager.broadcast_analysis_update(
            self.analysis_id,
            status,
            100.0 if success else 0.0,
            message
        )


def create_agent_notifier(analysis_id: str) -> AgentWebSocketNotifier:
    """Create a WebSocket notifier for an analysis"""
    return AgentWebSocketNotifier(analysis_id)