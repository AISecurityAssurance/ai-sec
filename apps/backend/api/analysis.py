"""
Analysis API routes
Handles analysis requests and orchestrates agent execution
"""
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime
import asyncio
import logging

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from core.database import get_db
from core.models.database import Analysis, AnalysisResult as DBAnalysisResult
from core.models.schemas import (
    AnalysisStatus, FrameworkType, AgentContext,
    AnalysisResponse, AnalysisSectionResponse,
    AnalysisCreateRequest
)
from pydantic import BaseModel
from core.agents.framework_agents.stpa_sec import StpaSecAgent
from core.agents.websocket_integration import create_agent_notifier
from core.websocket import manager
from config.settings import settings
from core.context import context_manager

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateAnalysisRequest(BaseModel):
    """Request to create a new analysis"""
    project_id: UUID
    system_description: str
    frameworks: List[FrameworkType]
    section_ids: Optional[Dict[str, List[str]]] = Field(
        None,
        description="Specific sections to analyze per framework"
    )
    metadata: Optional[Dict[str, Any]] = None


class UpdateAnalysisRequest(BaseModel):
    """Request to update analysis parameters"""
    system_description: Optional[str] = None
    frameworks: Optional[List[FrameworkType]] = None
    section_ids: Optional[Dict[str, List[str]]] = None


class SimpleAnalysisResponse(BaseModel):
    """Simple analysis response for creation"""
    id: UUID
    project_id: UUID
    status: AnalysisStatus
    frameworks: List[str]
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# Import agents
from core.agents.framework_agents.stpa_sec import StpaSecAgent
from core.agents.framework_agents.stride import StrideAgent
from core.agents.framework_agents.pasta import PastaAgent
from core.agents.framework_agents.dread import DreadAgent
from core.agents.framework_agents.maestro import MaestroAgent
from core.agents.framework_agents.linddun import LinddunAgent
from core.agents.framework_agents.hazop import HazopAgent
from core.agents.framework_agents.octave import OctaveAgent

# Agent registry
AGENT_REGISTRY = {
    FrameworkType.STPA_SEC: StpaSecAgent,
    FrameworkType.STRIDE: StrideAgent,
    FrameworkType.PASTA: PastaAgent,
    FrameworkType.DREAD: DreadAgent,
    FrameworkType.MAESTRO: MaestroAgent,
    FrameworkType.LINDDUN: LinddunAgent,
    FrameworkType.HAZOP: HazopAgent,
    FrameworkType.OCTAVE: OctaveAgent,
}


async def run_analysis_task(
    analysis_id: str,
    context: AgentContext,
    frameworks: List[FrameworkType],
    section_ids: Optional[Dict[str, List[str]]] = None
):
    """Background task to run analysis"""
    logger.info(f"Background task started for analysis {analysis_id}")
    from core.database import async_session_maker
    notifier = create_agent_notifier(analysis_id)
    
    async with async_session_maker() as db:
        try:
            logger.info(f"Updating analysis status to IN_PROGRESS for {analysis_id}")
            # Update analysis status
            analysis = await db.get(Analysis, analysis_id)
            analysis.status = AnalysisStatus.IN_PROGRESS
            analysis.started_at = datetime.utcnow()
            await db.commit()
            
            # Run each framework agent
            for framework in frameworks:
                agent_class = AGENT_REGISTRY.get(framework)
                if not agent_class:
                    logger.warning(f"No agent found for framework: {framework}")
                    continue
                    
                try:
                    # Pass database session to STPA-Sec agent
                    if framework == FrameworkType.STPA_SEC:
                        agent = agent_class(db_session=db)
                    else:
                        agent = agent_class()
                    
                    framework_sections = section_ids.get(framework.value) if section_ids else None
                    
                    # Run agent with WebSocket notifications
                    # Enable database saving for STPA-Sec
                    if framework == FrameworkType.STPA_SEC:
                        result = await agent.analyze(context, framework_sections, notifier, save_to_db=True)
                    else:
                        result = await agent.analyze(context, framework_sections, notifier)
                    
                    # Store result in database
                    db_result = DBAnalysisResult(
                        id=uuid4(),
                        analysis_id=analysis_id,
                        framework=framework,
                        sections=result.sections,
                        artifacts=result.artifacts,
                        duration=result.duration,
                        token_usage=result.token_usage
                    )
                    db.add(db_result)
                    
                except Exception as e:
                    logger.error(f"Error in {framework} agent: {e}", exc_info=True)
                    await notifier.notify_analysis_complete(
                        framework.value,
                        success=False,
                        error=str(e)
                    )
                    
            # Update analysis status
            analysis.status = AnalysisStatus.COMPLETED
            analysis.completed_at = datetime.utcnow()
            await db.commit()
            
            # Clean up context manager
            try:
                await context_manager.cleanup_analysis_context(UUID(analysis_id))
            except Exception as e:
                logger.warning(f"Failed to cleanup context manager: {e}")
            
        except Exception as e:
            logger.error(f"Error in analysis task: {e}", exc_info=True)
            # Update analysis status to failed
            analysis = await db.get(Analysis, analysis_id)
            if analysis:
                analysis.status = AnalysisStatus.FAILED
                analysis.error_message = str(e)
                await db.commit()
                
            # Clean up context manager on failure
            try:
                await context_manager.cleanup_analysis_context(UUID(analysis_id))
            except Exception as e:
                logger.warning(f"Failed to cleanup context manager: {e}")


@router.post("/", response_model=SimpleAnalysisResponse)
async def create_analysis(
    request: CreateAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Create and start a new analysis"""
    from core.models.database import Project, User
    
    # Check if project exists, if not create a default one
    project = await db.get(Project, request.project_id)
    if not project:
        # Create a default test user if needed
        from sqlalchemy import select
        result = await db.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            # Create a test user
            user = User(
                id=uuid4(),
                email="test@example.com",
                hashed_password="test",  # In real app, this would be hashed
                name="Test User",
                role="user"
            )
            db.add(user)
            await db.commit()
        
        # Create the project
        project = Project(
            id=request.project_id,
            name="Test Project",
            description="Auto-created project for testing",
            owner_id=user.id
        )
        db.add(project)
        await db.commit()
    
    # Create analysis record
    analysis = Analysis(
        id=uuid4(),
        project_id=request.project_id,
        system_description=request.system_description,
        frameworks=request.frameworks,
        status=AnalysisStatus.PENDING,
        metadata=request.metadata or {}
    )
    db.add(analysis)
    await db.commit()
    
    # Initialize context manager for this analysis
    try:
        context = await context_manager.initialize_analysis_context(
            analysis.id,
            request.system_description,
            existing_artifacts=None
        )
        context.metadata = request.metadata or {}
        context.metadata['project_id'] = str(request.project_id)
    except Exception as e:
        logger.warning(f"Failed to initialize context manager: {e}")
        # Fall back to basic context
        context = AgentContext(
            analysis_id=analysis.id,
            system_description=request.system_description,
            artifacts={},
            metadata={**(request.metadata or {}), 'project_id': str(request.project_id)}
        )
    
    # Start analysis in background
    logger.info(f"Starting background task for analysis {analysis.id}")
    background_tasks.add_task(
        run_analysis_task,
        str(analysis.id),
        context,
        request.frameworks,
        request.section_ids
    )
    logger.info(f"Background task queued for analysis {analysis.id}")
    
    return SimpleAnalysisResponse(
        id=analysis.id,
        project_id=analysis.project_id,
        status=analysis.status,
        frameworks=analysis.frameworks,
        created_at=analysis.created_at,
        started_at=analysis.started_at,
        completed_at=analysis.completed_at
    )


@router.get("/{analysis_id}", response_model=SimpleAnalysisResponse)
async def get_analysis(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get analysis status and metadata"""
    analysis = await db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    # Get results (not needed for simple response)
    # from sqlalchemy import select
    # result = await db.execute(
    #     select(DBAnalysisResult).where(DBAnalysisResult.analysis_id == analysis_id)
    # )
    # analysis_results = result.scalars().all()
    
    return SimpleAnalysisResponse(
        id=analysis.id,
        project_id=analysis.project_id,
        status=analysis.status,
        frameworks=analysis.frameworks,
        created_at=analysis.created_at,
        started_at=analysis.started_at,
        completed_at=analysis.completed_at
    )


@router.get("/{analysis_id}/sections", response_model=List[AnalysisSectionResponse])
async def get_analysis_sections(
    analysis_id: UUID,
    framework: Optional[FrameworkType] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get analysis sections for a specific framework or all frameworks"""
    query = db.query(DBAnalysisResult).filter_by(analysis_id=analysis_id)
    if framework:
        query = query.filter_by(framework=framework)
        
    results = await db.execute(query)
    analysis_results = results.scalars().all()
    
    sections = []
    for result in analysis_results:
        for section in result.sections:
            sections.append(AnalysisSectionResponse(
                framework=result.framework,
                section_id=section["section_id"],
                title=section["title"],
                status=section["status"],
                content=section.get("content"),
                template_type=section.get("template_type"),
                error=section.get("error")
            ))
            
    return sections


@router.patch("/{analysis_id}")
async def update_analysis(
    analysis_id: UUID,
    request: UpdateAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update analysis parameters (only if pending)"""
    analysis = await db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    if analysis.status != AnalysisStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Can only update pending analyses"
        )
        
    # Update fields
    if request.system_description:
        analysis.system_description = request.system_description
    if request.frameworks:
        analysis.frameworks = request.frameworks
        
    await db.commit()
    
    return {"message": "Analysis updated"}


@router.delete("/{analysis_id}")
async def cancel_analysis(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Cancel a running analysis"""
    analysis = await db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
        
    if analysis.status not in [AnalysisStatus.PENDING, AnalysisStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=400,
            detail="Can only cancel pending or in-progress analyses"
        )
        
    # Update status
    analysis.status = AnalysisStatus.CANCELLED
    await db.commit()
    
    # Notify via WebSocket
    await manager.broadcast_analysis_update(
        str(analysis_id),
        AnalysisStatus.CANCELLED,
        0.0,
        "Analysis cancelled by user"
    )
    
    return {"message": "Analysis cancelled"}


@router.get("/{analysis_id}/context")
async def get_analysis_context(
    analysis_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get context manager status for an analysis"""
    # Check if analysis exists
    analysis = await db.get(Analysis, analysis_id)
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    # Get context stats
    stats = context_manager.get_context_stats(analysis_id)
    
    return {
        "analysis_id": analysis_id,
        "context_status": stats
    }


@router.get("/{analysis_id}/export")
async def export_analysis(
    analysis_id: UUID,
    format: str = "json",
    db: AsyncSession = Depends(get_db)
):
    """Export analysis results in various formats"""
    # TODO: Implement export functionality
    # Formats: json, pdf, markdown, csv
    raise HTTPException(status_code=501, detail="Export not yet implemented")