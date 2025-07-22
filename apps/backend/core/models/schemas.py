from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, validator
from enum import Enum


# Enums (matching database models)
class AnalysisStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FrameworkType(str, Enum):
    STPA_SEC = "stpa-sec"
    STRIDE = "stride"
    PASTA = "pasta"
    DREAD = "dread"
    MAESTRO = "maestro"
    LINDDUN = "linddun"
    HAZOP = "hazop"
    OCTAVE = "octave"


class TemplateType(str, Enum):
    """Frontend template types"""
    TABLE = "table"
    CHART = "chart"
    DIAGRAM = "diagram"
    TEXT = "text"
    LIST = "list"
    FLOW = "flow"
    SECTION = "section"


# Request/Response Models
class AnalysisCreateRequest(BaseModel):
    """Request to create a new analysis"""
    title: str
    description: Optional[str] = None
    system_description: str
    selected_frameworks: List[FrameworkType]
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AnalysisSectionUpdate(BaseModel):
    """Request to update an analysis section"""
    content: Dict[str, Any]
    is_locked: Optional[bool] = None
    user_modifications: Optional[Dict[str, Any]] = None


class AnalysisQueryRequest(BaseModel):
    """Request to query analysis results"""
    query: str
    frameworks: Optional[List[FrameworkType]] = None
    include_artifacts: bool = False


class WebSocketMessage(BaseModel):
    """WebSocket message format"""
    type: str  # "status", "progress", "section_complete", "error"
    data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Response Models
class AnalysisSectionResponse(BaseModel):
    """Analysis section response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    framework: str
    section_id: str
    title: str
    content: Dict[str, Any]
    template_type: Optional[str]
    status: AnalysisStatus
    error_message: Optional[str]
    is_locked: bool
    created_at: datetime
    updated_at: Optional[datetime]


class ArtifactResponse(BaseModel):
    """Artifact response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    type: str
    format: Optional[str]
    content: Optional[Dict[str, Any]]
    file_path: Optional[str]
    source_framework: Optional[str]
    source_section: Optional[str]
    metadata: Dict[str, Any]
    created_at: datetime


class AnalysisResponse(BaseModel):
    """Full analysis response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    description: Optional[str]
    system_description: str
    status: AnalysisStatus
    progress: int
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    selected_frameworks: List[str]
    config: Dict[str, Any]
    total_duration: Optional[float]
    token_usage: Dict[str, Any]
    sections: List[AnalysisSectionResponse]
    artifacts: List[ArtifactResponse]


class AnalysisSummaryResponse(BaseModel):
    """Summary analysis response (for lists)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    title: str
    description: Optional[str]
    status: AnalysisStatus
    progress: int
    created_at: datetime
    updated_at: Optional[datetime]
    selected_frameworks: List[str]


# Template-specific schemas (matching frontend)
class TableColumn(BaseModel):
    """Table column definition"""
    key: str
    label: str
    type: str = "text"  # text, number, date, dropdown, etc.
    editable: bool = False
    options: Optional[List[str]] = None


class TableData(BaseModel):
    """Table template data"""
    columns: List[TableColumn]
    rows: List[Dict[str, Any]]
    editable: bool = False
    sortable: bool = True
    filterable: bool = True


class ChartData(BaseModel):
    """Chart template data"""
    type: str  # bar, pie, line, etc.
    labels: List[str]
    datasets: List[Dict[str, Any]]
    options: Optional[Dict[str, Any]] = None


class DiagramNode(BaseModel):
    """Diagram node"""
    id: str
    label: str
    type: Optional[str] = None
    position: Optional[Dict[str, float]] = None
    data: Optional[Dict[str, Any]] = None


class DiagramEdge(BaseModel):
    """Diagram edge"""
    id: str
    source: str
    target: str
    label: Optional[str] = None
    type: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class DiagramData(BaseModel):
    """Diagram template data"""
    nodes: List[DiagramNode]
    edges: List[DiagramEdge]
    layout: Optional[str] = "hierarchical"


# Agent communication schemas
class AgentContext(BaseModel):
    """Context passed between agents"""
    analysis_id: UUID
    system_description: str
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    completed_frameworks: List[FrameworkType] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    """Result from an agent"""
    framework: FrameworkType
    sections: List[Dict[str, Any]]  # List of section data
    artifacts: List[Dict[str, Any]] = Field(default_factory=list)
    duration: float
    token_usage: Dict[str, int]
    error: Optional[str] = None


# Performance tracking
class PerformanceMetricsResponse(BaseModel):
    """Performance metrics response"""
    analysis_times: Dict[str, List[float]]
    average_times: Dict[str, float]
    token_usage: Dict[str, Dict[str, int]]
    cache_hit_rate: float
    active_analyses: int


# Template mapping helpers
def create_table_content(data: TableData) -> Dict[str, Any]:
    """Create content for table template"""
    return {
        "template_type": "table",
        "data": data.model_dump()
    }


def create_chart_content(data: ChartData) -> Dict[str, Any]:
    """Create content for chart template"""
    return {
        "template_type": "chart",
        "data": data.model_dump()
    }


def create_diagram_content(data: DiagramData) -> Dict[str, Any]:
    """Create content for diagram template"""
    return {
        "template_type": "diagram",
        "data": data.model_dump()
    }


def create_text_content(content: str, format: str = "markdown") -> Dict[str, Any]:
    """Create content for text template"""
    return {
        "template_type": "text",
        "data": {
            "content": content,
            "format": format
        }
    }


def create_list_content(items: List[Dict[str, Any]], ordered: bool = False) -> Dict[str, Any]:
    """Create content for list template"""
    return {
        "template_type": "list",
        "data": {
            "items": items,
            "ordered": ordered
        }
    }