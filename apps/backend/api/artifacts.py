"""
Artifacts API routes
Manages analysis artifacts and cross-references
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel

from core.database import get_db
from core.models.database import AnalysisResult, Artifact
from core.models.schemas import FrameworkType

logger = logging.getLogger(__name__)

router = APIRouter()


class ArtifactResponse(BaseModel):
    """Artifact response model"""
    id: UUID
    analysis_id: UUID
    framework: FrameworkType
    artifact_type: str
    name: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]


class CreateArtifactRequest(BaseModel):
    """Request to create a new artifact"""
    analysis_id: UUID
    framework: FrameworkType
    artifact_type: str
    name: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


@router.get("/analysis/{analysis_id}", response_model=List[ArtifactResponse])
async def get_analysis_artifacts(
    analysis_id: UUID,
    framework: Optional[FrameworkType] = None,
    artifact_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all artifacts for an analysis"""
    # Build query
    query = select(Artifact).where(Artifact.analysis_id == analysis_id)
    
    if framework:
        query = query.where(Artifact.framework == framework)
    if artifact_type:
        query = query.where(Artifact.artifact_type == artifact_type)
        
    # Execute query
    result = await db.execute(query)
    artifacts = result.scalars().all()
    
    return [
        ArtifactResponse(
            id=artifact.id,
            analysis_id=artifact.analysis_id,
            framework=artifact.framework,
            artifact_type=artifact.artifact_type,
            name=artifact.name,
            data=artifact.data,
            metadata=artifact.metadata
        )
        for artifact in artifacts
    ]


@router.get("/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(
    artifact_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific artifact"""
    artifact = await db.get(Artifact, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    return ArtifactResponse(
        id=artifact.id,
        analysis_id=artifact.analysis_id,
        framework=artifact.framework,
        artifact_type=artifact.artifact_type,
        name=artifact.name,
        data=artifact.data,
        metadata=artifact.metadata
    )


@router.post("/", response_model=ArtifactResponse)
async def create_artifact(
    request: CreateArtifactRequest,
    db: AsyncSession = Depends(get_db)
):
    """Create a new artifact"""
    artifact = Artifact(
        analysis_id=request.analysis_id,
        framework=request.framework,
        artifact_type=request.artifact_type,
        name=request.name,
        data=request.data,
        metadata=request.metadata or {}
    )
    
    db.add(artifact)
    await db.commit()
    await db.refresh(artifact)
    
    return ArtifactResponse(
        id=artifact.id,
        analysis_id=artifact.analysis_id,
        framework=artifact.framework,
        artifact_type=artifact.artifact_type,
        name=artifact.name,
        data=artifact.data,
        metadata=artifact.metadata
    )


@router.get("/cross-reference/{analysis_id}")
async def get_cross_references(
    analysis_id: UUID,
    source_framework: FrameworkType,
    target_framework: FrameworkType,
    db: AsyncSession = Depends(get_db)
):
    """Get cross-references between frameworks"""
    # Get artifacts from both frameworks
    source_artifacts = await db.execute(
        select(Artifact).where(
            Artifact.analysis_id == analysis_id,
            Artifact.framework == source_framework
        )
    )
    source_artifacts = source_artifacts.scalars().all()
    
    target_artifacts = await db.execute(
        select(Artifact).where(
            Artifact.analysis_id == analysis_id,
            Artifact.framework == target_framework
        )
    )
    target_artifacts = target_artifacts.scalars().all()
    
    # Build cross-references based on artifact types
    cross_refs = []
    
    # Example: Link STPA-Sec hazards to STRIDE threats
    if source_framework == FrameworkType.STPA_SEC and target_framework == FrameworkType.STRIDE:
        hazards = [a for a in source_artifacts if a.artifact_type == "hazards"]
        threats = [a for a in target_artifacts if a.artifact_type == "threats"]
        
        for hazard in hazards:
            for threat in threats:
                # Simple keyword matching - could be enhanced with ML
                if any(keyword in str(threat.data).lower() 
                      for keyword in str(hazard.data).lower().split()):
                    cross_refs.append({
                        "source": {
                            "framework": source_framework,
                            "artifact_id": hazard.id,
                            "name": hazard.name,
                            "type": hazard.artifact_type
                        },
                        "target": {
                            "framework": target_framework,
                            "artifact_id": threat.id,
                            "name": threat.name,
                            "type": threat.artifact_type
                        },
                        "confidence": 0.7  # Could calculate based on match strength
                    })
                    
    return {"cross_references": cross_refs}


@router.delete("/{artifact_id}")
async def delete_artifact(
    artifact_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Delete an artifact"""
    artifact = await db.get(Artifact, artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")
        
    await db.delete(artifact)
    await db.commit()
    
    return {"message": "Artifact deleted"}