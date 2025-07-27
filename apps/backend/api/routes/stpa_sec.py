"""
STPA-Sec specific API routes for database operations
"""
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from .stpa_sec_db import get_sync_db
from storage.repositories.stpa_sec import STPASecRepository
from src.database.stpa_sec_models import (
    SystemDefinition, Loss, Hazard, Entity, Relationship,
    Scenario, Mitigation, Adversary, ScenarioMitigation
)
from pydantic import BaseModel


router = APIRouter(prefix="/stpa-sec", tags=["STPA-Sec"])


# Pydantic models for API responses
class SystemDefinitionResponse(BaseModel):
    id: str
    mission_statement: Dict[str, Any]
    system_boundaries: Optional[Dict[str, Any]]
    operational_context: Optional[Dict[str, Any]]
    
    class Config:
        from_attributes = True


class LossResponse(BaseModel):
    id: str
    description: str
    impact_type: Optional[str]
    severity: str
    stakeholder_refs: List[str]
    
    class Config:
        from_attributes = True


class HazardResponse(BaseModel):
    id: str
    description: str
    loss_refs: List[str]
    worst_case_scenario: Optional[str]
    likelihood: Optional[str]
    detection_difficulty: Optional[str]
    
    class Config:
        from_attributes = True


class EntityResponse(BaseModel):
    id: str
    name: str
    type: str
    description: str
    responsibilities: List[str]
    
    class Config:
        from_attributes = True


class RelationshipResponse(BaseModel):
    id: str
    source_id: str
    target_id: str
    type: str
    control_actions: List[str]
    feedback_info: List[str]
    
    class Config:
        from_attributes = True


class ScenarioResponse(BaseModel):
    id: str
    description: str
    likelihood: Optional[str]
    impact: Optional[str]
    hazard_refs: List[str]
    threat_actor_refs: Optional[List[str]]
    attack_chain: Optional[List[str]]
    
    class Config:
        from_attributes = True


class MitigationResponse(BaseModel):
    id: str
    name: str
    description: str
    type: str
    effectiveness: str
    
    class Config:
        from_attributes = True


@router.get("/system-definition", response_model=Optional[SystemDefinitionResponse])
async def get_system_definition(db: Session = Depends(get_sync_db)):
    """Get the current system definition"""
    repo = STPASecRepository(db)
    system_def = repo.get_system_definition()
    return system_def


@router.get("/losses", response_model=List[LossResponse])
async def get_losses(
    stakeholder_id: Optional[str] = Query(None, description="Filter by stakeholder"),
    db: Session = Depends(get_sync_db)
):
    """Get all losses, optionally filtered by stakeholder"""
    repo = STPASecRepository(db)
    
    if stakeholder_id:
        losses = repo.get_losses_for_stakeholder(stakeholder_id)
    else:
        losses = db.query(Loss).all()
    
    return losses


@router.get("/hazards", response_model=List[HazardResponse])
async def get_hazards(
    loss_id: Optional[str] = Query(None, description="Filter by loss"),
    db: Session = Depends(get_sync_db)
):
    """Get all hazards, optionally filtered by loss"""
    repo = STPASecRepository(db)
    
    if loss_id:
        hazards = repo.get_hazards_for_loss(loss_id)
    else:
        hazards = db.query(Hazard).all()
    
    return hazards


@router.get("/control-structure", response_model=Dict[str, Any])
async def get_control_structure(db: Session = Depends(get_sync_db)):
    """Get the complete control structure with entities and relationships"""
    repo = STPASecRepository(db)
    control_structure = repo.get_control_structure()
    return control_structure


@router.get("/entities", response_model=List[EntityResponse])
async def get_entities(
    entity_type: Optional[str] = Query(None, description="Filter by type: controller, actuator, sensor, process"),
    db: Session = Depends(get_sync_db)
):
    """Get all entities in the control structure"""
    query = db.query(Entity)
    
    # Filter by type from properties JSON field if specified
    if entity_type:
        query = query.filter(Entity.properties['type'].astext == entity_type.lower())
    
    entities = query.all()
    
    # Transform entities to match the response model
    entity_responses = []
    for entity in entities:
        entity_data = {
            "id": entity.id,
            "name": entity.name,
            "description": entity.description,
            "type": entity.properties.get('type', 'unknown') if entity.properties else 'unknown',
            "responsibilities": entity.properties.get('responsibilities', []) if entity.properties else []
        }
        entity_responses.append(EntityResponse(**entity_data))
    
    return entity_responses


@router.get("/relationships", response_model=List[RelationshipResponse])
async def get_relationships(
    entity_id: Optional[str] = Query(None, description="Filter by entity (as source or target)"),
    relationship_type: Optional[str] = Query(None, description="Filter by type: control, feedback"),
    db: Session = Depends(get_sync_db)
):
    """Get relationships between entities"""
    query = db.query(Relationship)
    
    if entity_id:
        query = query.filter(
            (Relationship.source_id == entity_id) | 
            (Relationship.target_id == entity_id)
        )
    
    if relationship_type:
        query = query.filter(Relationship.type == relationship_type.lower())
    
    relationships = query.all()
    return relationships


@router.get("/scenarios", response_model=List[ScenarioResponse])
async def get_scenarios(
    likelihood: Optional[str] = Query(None, description="Filter by likelihood"),
    impact: Optional[str] = Query(None, description="Filter by impact"),
    db: Session = Depends(get_sync_db)
):
    """Get loss scenarios, optionally filtered by risk parameters"""
    query = db.query(Scenario)
    
    if likelihood:
        query = query.filter(Scenario.likelihood == likelihood.lower())
    
    if impact:
        query = query.filter(Scenario.impact == impact.lower())
    
    scenarios = query.all()
    
    return scenarios


@router.get("/mitigations", response_model=List[MitigationResponse])
async def get_mitigations(
    scenario_id: Optional[str] = Query(None, description="Filter by scenario"),
    effectiveness: Optional[str] = Query(None, description="Filter by effectiveness"),
    db: Session = Depends(get_sync_db)
):
    """Get mitigations, optionally filtered"""
    query = db.query(Mitigation)
    
    if scenario_id:
        # Join with ScenarioMitigation to filter by scenario
        query = query.join(ScenarioMitigation).filter(
            ScenarioMitigation.scenario_id == scenario_id
        )
    
    if effectiveness:
        query = query.filter(Mitigation.effectiveness == effectiveness.lower())
    
    mitigations = query.all()
    return mitigations


@router.get("/adversaries", response_model=List[Dict[str, Any]])
async def get_adversaries(
    sophistication: Optional[str] = Query(None, description="Filter by sophistication level"),
    db: Session = Depends(get_sync_db)
):
    """Get adversary profiles"""
    query = db.query(Adversary)
    
    if sophistication:
        query = query.filter(Adversary.technical_sophistication == sophistication.lower())
    
    adversaries = query.all()
    
    return [
        {
            "id": adv.id,
            "name": adv.name,
            "type": adv.type,
            "technical_sophistication": adv.technical_sophistication,
            "resources": adv.resources,
            "primary_motivation": adv.primary_motivation,
            "capabilities": adv.capabilities,
            "ttps": adv.ttps
        }
        for adv in adversaries
    ]


@router.get("/risk-summary", response_model=Dict[str, Any])
async def get_risk_summary(db: Session = Depends(get_sync_db)):
    """Get a summary of the current risk posture"""
    # Count critical items
    critical_hazards = db.query(Hazard).count()
    high_risk_scenarios = db.query(Scenario).filter(
        (Scenario.impact == 'catastrophic') | (Scenario.impact == 'major')
    ).count()
    
    total_scenarios = db.query(Scenario).count()
    total_mitigations = db.query(Mitigation).count()
    
    # Risk distribution
    risk_distribution = {
        "critical": db.query(Scenario).filter(Scenario.impact == 'catastrophic').count(),
        "high": db.query(Scenario).filter(Scenario.impact == 'major').count(),
        "medium": db.query(Scenario).filter(Scenario.impact == 'moderate').count(),
        "low": db.query(Scenario).filter(Scenario.impact == 'minor').count(),
    }
    
    # Mitigation coverage
    mitigated_scenarios = db.query(ScenarioMitigation.scenario_id).distinct().count()
    coverage_percentage = (mitigated_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0
    
    # Get top risks and convert to dictionaries
    top_risk_scenarios = db.query(Scenario).filter(
        (Scenario.impact == 'catastrophic') | (Scenario.impact == 'major')
    ).limit(5).all()
    
    top_risks = [
        {
            "scenario_id": scenario.id,
            "description": scenario.description,
            "impact": scenario.impact,
            "likelihood": scenario.likelihood
        }
        for scenario in top_risk_scenarios
    ]
    
    return {
        "summary": {
            "total_hazards": critical_hazards,
            "high_risk_scenarios": high_risk_scenarios,
            "total_scenarios": total_scenarios,
            "total_mitigations": total_mitigations,
            "mitigation_coverage": coverage_percentage
        },
        "risk_distribution": risk_distribution,
        "top_risks": top_risks
    }


@router.post("/export")
async def export_analysis(
    format: str = Query("json", description="Export format: json, csv, markdown"),
    db: Session = Depends(get_sync_db)
):
    """Export STPA-Sec analysis in various formats"""
    # TODO: Implement export functionality
    return {
        "message": "Export functionality not yet implemented",
        "requested_format": format
    }


# Include Step 1 specific routes
from api.stpa_sec_step1 import router as step1_router
router.include_router(step1_router, prefix="/step1", tags=["STPA-Sec Step 1"])