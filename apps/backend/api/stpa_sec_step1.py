"""Step 1 specific API endpoints - Fixed for SQLAlchemy"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks, WebSocket
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
from uuid import uuid4
from datetime import datetime
import json
from sqlalchemy import text, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.agents.step1_agents import Step1Coordinator
from core.websocket.manager import manager as websocket_manager
from api.auth_optional import get_current_user
from core.models.database import User

router = APIRouter()


class Step1RunRequest(BaseModel):
    system_description: str
    analysis_name: str
    execution_mode: str = "standard"  # standard, multi_pass
    preserved_elements: Optional[Dict[str, Any]] = None
    model_preset: Optional[str] = None  # default, fast, quality, local


class ElementEditRequest(BaseModel):
    changes: Dict[str, Any]
    freeze: bool = False


class CommitDraftRequest(BaseModel):
    commit_message: Optional[str] = None


@router.post("/analyses/{analysis_id}/step1/run")
async def run_step1_analysis(
    analysis_id: str,
    request: Step1RunRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Run Step 1 analysis using existing coordinator"""
    
    # Verify analysis exists and user has access
    result = await db.execute(
        text("SELECT * FROM step1_analyses WHERE id = :id"),
        {"id": analysis_id}
    )
    analysis = result.first()
    if not analysis:
        # Create the analysis if it doesn't exist
        await db.execute(
            text("""
                INSERT INTO step1_analyses (id, name, description, system_type, created_at)
                VALUES (:id, :name, :description, 'general', NOW())
            """),
            {
                "id": analysis_id,
                "name": request.analysis_name,
                "description": request.system_description
            }
        )
        await db.commit()
    
    # Create or get draft
    draft_id = await get_or_create_draft(db, analysis_id, current_user.id)
    
    # Progress callback for WebSocket updates
    async def progress_callback(agent_name: str, status_msg: str):
        # For now, just log the progress since WebSocket requires specific format
        # In future, we can enhance the WebSocket manager
        print(f"[Step 1 Progress] {agent_name}: {status_msg}")
    
    # Run analysis in background
    background_tasks.add_task(
        run_step1_with_progress,
        analysis_id,
        request.system_description,
        request.analysis_name,
        progress_callback,
        request.preserved_elements,
        request.model_preset,
        request.execution_mode
    )
    
    return {
        "analysis_id": analysis_id,
        "draft_id": draft_id,
        "status": "processing"
    }


async def run_step1_with_progress(
    analysis_id: str,
    system_description: str,
    analysis_name: str,
    progress_callback,
    preserved_elements: Optional[Dict] = None,
    model_preset: Optional[str] = None,
    execution_mode: str = "standard"
):
    """Run Step 1 with progress updates"""
    try:
        # Notify start
        await progress_callback("initialization", "Starting Step 1 analysis...")
        
        # Create asyncpg connection for the coordinator
        import asyncpg
        DATABASE_URL = "postgresql://sa_user:sa_password@postgres:5432/security_analyst"
        db_conn = await asyncpg.connect(DATABASE_URL)
        
        # Initialize coordinator with asyncpg connection and execution mode
        coordinator = Step1Coordinator(analysis_id, db_conn, execution_mode)
        
        # Add progress hooks to coordinator
        original_log = coordinator._log_execution
        
        async def log_with_progress(message: str, error: bool = False):
            # Call original log
            original_log(message, error)
            # Send progress update
            if not error:
                await progress_callback("execution", message)
        
        coordinator._log_execution = log_with_progress
        
        # Run analysis with existing method
        results = await coordinator.perform_analysis(
            system_description,
            analysis_name
        )
        
        # If we have preserved elements, merge them
        if preserved_elements:
            results = merge_preserved_elements(results, preserved_elements)
        
        # Track dependencies for future impact analysis
        # await track_dependencies(db, analysis_id, results)
        
        # Notify completion
        await progress_callback("complete", "Analysis complete")
        
        # Log completion
        print(f"[Step 1 Complete] Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        await progress_callback("error", f"Analysis failed: {str(e)}")
        # Log error to database would go here
        raise
    finally:
        # Close the database connection
        if 'db_conn' in locals():
            await db_conn.close()


@router.put("/analyses/{analysis_id}/elements/{element_type}/{element_id}")
async def edit_element(
    analysis_id: str,
    element_type: str,
    element_id: str,
    request: ElementEditRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Edit an element and save to draft"""
    
    # Validate element type
    valid_types = ['loss', 'hazard', 'stakeholder', 'problem_statement']
    if element_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid element type: {element_type}")
    
    # Verify element exists
    table_map = {
        'loss': 'step1_losses',
        'hazard': 'step1_hazards',
        'stakeholder': 'step1_stakeholders',
        'problem_statement': 'problem_statements'
    }
    
    table = table_map[element_type]
    result = await db.execute(
        text(f"SELECT * FROM {table} WHERE id = :id AND analysis_id = :analysis_id"),
        {"id": element_id, "analysis_id": analysis_id}
    )
    element = result.first()
    if not element:
        raise HTTPException(status_code=404, detail=f"{element_type} not found")
    
    # Get or create draft
    draft_id = await get_or_create_draft(db, analysis_id, current_user.id)
    
    # Get impact analysis
    impact = await analyze_edit_impact(db, element_type, element_id)
    
    # Save edit to draft
    await accumulate_edit_in_draft(
        db, 
        draft_id,
        element_type,
        element_id,
        request.changes,
        request.freeze
    )
    
    return {
        "draft_id": draft_id,
        "status": "saved_to_draft",
        "impact": impact,
        "freeze": request.freeze
    }


@router.post("/analyses/{analysis_id}/drafts/{draft_id}/commit")
async def commit_draft(
    analysis_id: str,
    draft_id: str,
    request: CommitDraftRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Commit draft as new version"""
    
    # Verify draft exists and belongs to user
    result = await db.execute(
        text("""
            SELECT * FROM analysis_drafts 
            WHERE id = :draft_id AND analysis_id = :analysis_id 
            AND user_id = :user_id AND status = 'working'
        """),
        {
            "draft_id": draft_id,
            "analysis_id": analysis_id,
            "user_id": current_user.id
        }
    )
    draft = result.first()
    
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found or already committed")
    
    # Apply all draft edits to database
    version_id = await commit_draft_to_version(
        db,
        draft_id,
        analysis_id,
        request.commit_message,
        current_user.id
    )
    
    return {
        "version_id": version_id,
        "status": "committed"
    }


@router.get("/analyses/{analysis_id}/drafts")
async def get_user_drafts(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's drafts for an analysis"""
    
    result = await db.execute(
        text("""
            SELECT 
                id,
                status,
                created_at,
                updated_at,
                jsonb_array_length(COALESCE(draft_data->'edits', '[]'::jsonb)) as edit_count
            FROM analysis_drafts
            WHERE analysis_id = :analysis_id AND user_id = :user_id
            ORDER BY created_at DESC
        """),
        {"analysis_id": analysis_id, "user_id": current_user.id}
    )
    drafts = result.fetchall()
    
    return {
        "drafts": [dict(d._mapping) for d in drafts]
    }


@router.get("/analyses/{analysis_id}/versions")
async def get_analysis_versions(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get version history for an analysis"""
    
    result = await db.execute(
        text("""
            SELECT 
                id,
                version_number,
                version_type,
                commit_message,
                created_by,
                created_at,
                jsonb_array_length(COALESCE(user_modifications, '{}'::jsonb)) as modification_count
            FROM analysis_versions
            WHERE analysis_id = :analysis_id
            ORDER BY version_number DESC
            LIMIT 20
        """),
        {"analysis_id": analysis_id}
    )
    versions = result.fetchall()
    
    return {
        "versions": [dict(v._mapping) for v in versions]
    }


# Helper functions
async def get_or_create_draft(db: AsyncSession, analysis_id: str, user_id: str) -> str:
    """Get existing working draft or create new one"""
    
    # Check for existing working draft
    result = await db.execute(
        text("""
            SELECT id FROM analysis_drafts
            WHERE analysis_id = :analysis_id 
            AND user_id = :user_id 
            AND status = 'working'
            ORDER BY created_at DESC
            LIMIT 1
        """),
        {"analysis_id": analysis_id, "user_id": user_id}
    )
    existing = result.first()
    
    if existing:
        return existing.id
    
    # Create new draft
    draft_id = str(uuid4())
    await db.execute(
        text("""
            INSERT INTO analysis_drafts (id, analysis_id, user_id, status, draft_data, created_at, updated_at)
            VALUES (:id, :analysis_id, :user_id, 'working', '{}', NOW(), NOW())
        """),
        {
            "id": draft_id,
            "analysis_id": analysis_id,
            "user_id": user_id
        }
    )
    await db.commit()
    
    return draft_id


async def accumulate_edit_in_draft(
    db: AsyncSession, 
    draft_id: str,
    element_type: str,
    element_id: str,
    changes: Dict[str, Any],
    freeze: bool = False
):
    """Add edit to draft data"""
    
    # Get current draft data
    result = await db.execute(
        text("SELECT draft_data FROM analysis_drafts WHERE id = :id"),
        {"id": draft_id}
    )
    draft = result.first()
    
    draft_data = draft.draft_data or {}
    
    # Initialize structure if needed
    if 'edits' not in draft_data:
        draft_data['edits'] = {}
    if element_type not in draft_data['edits']:
        draft_data['edits'][element_type] = {}
    
    # Add edit
    draft_data['edits'][element_type][element_id] = {
        'changes': changes,
        'freeze': freeze,
        'edited_at': datetime.now().isoformat()
    }
    
    # Update draft
    await db.execute(
        text("""
            UPDATE analysis_drafts 
            SET draft_data = :data, updated_at = NOW()
            WHERE id = :id
        """),
        {"data": json.dumps(draft_data), "id": draft_id}
    )
    await db.commit()


async def analyze_edit_impact(
    db: AsyncSession,
    element_type: str,
    element_id: str
) -> Dict[str, Any]:
    """Analyze impact of editing an element"""
    
    # Get dependencies
    result = await db.execute(
        text("""
            SELECT dependent_type, dependent_id, dependency_strength
            FROM element_dependencies
            WHERE source_type = :source_type AND source_id = :source_id
        """),
        {"source_type": element_type, "source_id": element_id}
    )
    deps = result.fetchall()
    
    # Get specific impact details based on element type
    impact_details = []
    
    if element_type == 'loss':
        # Editing a loss affects hazards
        hazard_count = sum(1 for d in deps if d.dependent_type == 'hazard')
        if hazard_count > 0:
            impact_details.append(f"{hazard_count} hazards reference this loss")
    
    elif element_type == 'hazard':
        # Editing a hazard affects scenarios in Step 3
        impact_details.append("Scenarios in Step 3 may need review")
    
    return {
        "affected_count": len(deps),
        "affected_elements": [
            {
                "type": d.dependent_type,
                "id": d.dependent_id,
                "strength": d.dependency_strength
            }
            for d in deps
        ],
        "severity": "high" if len(deps) > 5 else "medium" if len(deps) > 0 else "low",
        "details": impact_details
    }


async def commit_draft_to_version(
    db: AsyncSession,
    draft_id: str,
    analysis_id: str,
    commit_message: Optional[str],
    user_id: str
) -> str:
    """Commit draft to a new version"""
    
    # Get draft data
    result = await db.execute(
        text("SELECT draft_data FROM analysis_drafts WHERE id = :id"),
        {"id": draft_id}
    )
    draft = result.first()
    
    draft_data = draft.draft_data or {}
    edits = draft_data.get('edits', {})
    
    # Apply edits to actual tables
    for element_type, elements in edits.items():
        table_map = {
            'loss': 'step1_losses',
            'hazard': 'step1_hazards',
            'stakeholder': 'step1_stakeholders',
            'problem_statement': 'problem_statements'
        }
        
        table = table_map.get(element_type)
        if not table:
            continue
        
        for element_id, edit_info in elements.items():
            changes = edit_info['changes']
            
            # Build UPDATE statement dynamically
            set_clauses = []
            params = {"id": element_id}
            for i, (field, value) in enumerate(changes.items(), 1):
                set_clauses.append(f"{field} = :val{i}")
                params[f"val{i}"] = value
            
            if set_clauses:
                query = f"""
                    UPDATE {table}
                    SET {', '.join(set_clauses)}, updated_at = NOW()
                    WHERE id = :id
                """
                await db.execute(text(query), params)
    
    # Get current version number
    result = await db.execute(
        text("""
            SELECT COALESCE(MAX(version_number), 0) as max_version
            FROM analysis_versions
            WHERE analysis_id = :analysis_id
        """),
        {"analysis_id": analysis_id}
    )
    current_version = result.first().max_version
    
    # Create version snapshot
    state_snapshot = {
        "edits": edits,
        "timestamp": datetime.now().isoformat()
    }
    
    # Create version record
    version_id = str(uuid4())
    await db.execute(
        text("""
            INSERT INTO analysis_versions 
            (id, analysis_id, version_number, version_type, state_snapshot, 
             user_modifications, commit_message, created_by, created_at)
            VALUES (:id, :analysis_id, :version_number, :version_type, :state_snapshot, 
                    :user_modifications, :commit_message, :created_by, NOW())
        """),
        {
            "id": version_id,
            "analysis_id": analysis_id,
            "version_number": current_version + 1,
            "version_type": 'user_save',
            "state_snapshot": json.dumps(state_snapshot),
            "user_modifications": json.dumps(edits),
            "commit_message": commit_message,
            "created_by": user_id
        }
    )
    
    # Update draft status
    await db.execute(
        text("""
            UPDATE analysis_drafts
            SET status = 'committed', 
                committed_at = NOW(),
                commit_version_id = :version_id
            WHERE id = :draft_id
        """),
        {"version_id": version_id, "draft_id": draft_id}
    )
    
    await db.commit()
    
    return version_id


def merge_preserved_elements(results: Dict[str, Any], preserved_elements: Dict[str, Any]) -> Dict[str, Any]:
    """Merge preserved elements with AI results"""
    
    # Deep copy results to avoid modifying original
    import copy
    merged = copy.deepcopy(results)
    
    # Merge each element type
    for element_type, elements in preserved_elements.items():
        if element_type in merged['results']:
            # Replace or add preserved elements
            result_list = merged['results'][element_type]
            
            # Create lookup by ID
            result_dict = {elem.get('id', elem.get('identifier')): elem for elem in result_list}
            
            # Override with preserved elements
            for elem_id, preserved_elem in elements.items():
                result_dict[elem_id] = preserved_elem
            
            # Convert back to list
            merged['results'][element_type] = list(result_dict.values())
    
    return merged