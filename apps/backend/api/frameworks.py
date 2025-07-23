"""
Framework-specific analysis endpoints
"""
from typing import Dict, Any, List, Optional
from uuid import uuid4
import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from core.database import get_db
from core.models.schemas import FrameworkType
from core.agents.framework_agents.stpa_sec import StpaSecAgent
from core.agents.framework_agents.stride import StrideAgent  
from core.agents.framework_agents.pasta import PastaAgent
from core.agents.framework_agents.dread import DreadAgent
from core.agents.framework_agents.maestro import MaestroAgent
from core.agents.framework_agents.linddun import LinddunAgent
from core.agents.framework_agents.hazop import HazopAgent
from core.agents.framework_agents.octave import OctaveAgent
from core.websocket import manager
from core.agents.websocket_integration import create_agent_notifier

logger = logging.getLogger(__name__)

router = APIRouter()


class FrameworkAnalysisRequest(BaseModel):
    """Request for framework-specific analysis"""
    user_id: str
    system_description: str
    components: List[str] = Field(default_factory=list)
    data_flows: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class FrameworkAnalysisResponse(BaseModel):
    """Response for framework analysis"""
    analysis_id: str
    framework: str
    status: str = "started"
    message: str = "Analysis started successfully"


# Agent mapping
FRAMEWORK_AGENTS = {
    FrameworkType.STPA_SEC: StpaSecAgent,
    FrameworkType.STRIDE: StrideAgent,
    FrameworkType.PASTA: PastaAgent,
    FrameworkType.DREAD: DreadAgent,
    FrameworkType.MAESTRO: MaestroAgent,
    FrameworkType.LINDDUN: LinddunAgent,
    FrameworkType.HAZOP: HazopAgent,
    FrameworkType.OCTAVE: OctaveAgent,
}


async def run_framework_analysis(
    framework: FrameworkType,
    request: FrameworkAnalysisRequest,
    db: AsyncSession
) -> FrameworkAnalysisResponse:
    """Run analysis for a specific framework"""
    analysis_id = str(uuid4())
    
    # Get the appropriate agent
    agent_class = FRAMEWORK_AGENTS.get(framework)
    if not agent_class:
        raise HTTPException(status_code=400, detail=f"Unknown framework: {framework}")
    
    # Create WebSocket notifier
    notifier = None
    if manager:
        notifier = await create_agent_notifier(
            manager,
            analysis_id,
            request.user_id,
            framework.value
        )
    
    # Initialize agent
    agent = agent_class(notifier=notifier)
    
    # Run analysis (in real implementation, this would be async/background)
    try:
        # For now, just return a mock response
        # In production, this would start a background task
        return FrameworkAnalysisResponse(
            analysis_id=analysis_id,
            framework=framework.value,
            status="started",
            message=f"{framework.value.upper()} analysis started"
        )
    except Exception as e:
        logger.error(f"Framework analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Create endpoints for each framework
@router.post("/stpa-sec", response_model=FrameworkAnalysisResponse)
async def analyze_stpa_sec(
    request: FrameworkAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run STPA-Sec analysis"""
    return await run_framework_analysis(FrameworkType.STPA_SEC, request, db)


@router.post("/stride", response_model=FrameworkAnalysisResponse)
async def analyze_stride(
    request: FrameworkAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run STRIDE analysis"""
    return await run_framework_analysis(FrameworkType.STRIDE, request, db)


@router.post("/pasta", response_model=FrameworkAnalysisResponse)
async def analyze_pasta(
    request: FrameworkAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run PASTA analysis"""
    return await run_framework_analysis(FrameworkType.PASTA, request, db)


@router.post("/dread", response_model=FrameworkAnalysisResponse)
async def analyze_dread(
    request: FrameworkAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run DREAD analysis"""
    return await run_framework_analysis(FrameworkType.DREAD, request, db)


@router.post("/maestro", response_model=FrameworkAnalysisResponse)
async def analyze_maestro(
    request: FrameworkAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run MAESTRO analysis"""
    return await run_framework_analysis(FrameworkType.MAESTRO, request, db)


@router.post("/linddun", response_model=FrameworkAnalysisResponse)
async def analyze_linddun(
    request: FrameworkAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run LINDDUN analysis"""
    return await run_framework_analysis(FrameworkType.LINDDUN, request, db)


@router.post("/hazop", response_model=FrameworkAnalysisResponse)
async def analyze_hazop(
    request: FrameworkAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run HAZOP analysis"""
    return await run_framework_analysis(FrameworkType.HAZOP, request, db)


@router.post("/octave", response_model=FrameworkAnalysisResponse)
async def analyze_octave(
    request: FrameworkAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Run OCTAVE analysis"""
    return await run_framework_analysis(FrameworkType.OCTAVE, request, db)