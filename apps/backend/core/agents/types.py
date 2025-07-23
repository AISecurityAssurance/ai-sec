"""
Common types and models for agents
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from core.models.schemas import AnalysisStatus, TemplateType


class SectionResult(BaseModel):
    """Result for a single analysis section"""
    section_id: str
    title: str
    content: Dict[str, Any]
    template_type: TemplateType
    status: AnalysisStatus = AnalysisStatus.PENDING
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    

class AnalysisProgress(BaseModel):
    """Progress update for analysis"""
    analysis_id: str
    framework: str
    current_section: str
    progress: int  # 0-100
    status: AnalysisStatus
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)