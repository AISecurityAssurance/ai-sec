"""
Tests for analysis API endpoints
"""
import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4
import json

from core.models.schemas import FrameworkType, AnalysisStatus


@pytest.mark.asyncio
async def test_create_analysis(async_client, test_project, override_get_db):
    """Test creating a new analysis"""
    request_data = {
        "project_id": str(test_project.id),
        "system_description": "Test banking system",
        "frameworks": ["STPA_SEC", "STRIDE"],
        "metadata": {"test": True}
    }
    
    with patch('api.analysis.run_analysis_task') as mock_task:
        response = await async_client.post("/api/analysis/", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data
    assert data["project_id"] == str(test_project.id)
    assert data["status"] == "pending"
    assert data["frameworks"] == ["STPA_SEC", "STRIDE"]


@pytest.mark.asyncio
async def test_get_analysis(async_client, test_analysis, override_get_db):
    """Test getting analysis details"""
    response = await async_client.get(f"/api/analysis/{test_analysis.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == str(test_analysis.id)
    assert data["project_id"] == str(test_analysis.project_id)
    assert data["status"] == test_analysis.status.value
    assert data["frameworks"] == [f.value for f in test_analysis.frameworks]


@pytest.mark.asyncio
async def test_get_analysis_not_found(async_client, override_get_db):
    """Test getting non-existent analysis"""
    fake_id = uuid4()
    response = await async_client.get(f"/api/analysis/{fake_id}")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Analysis not found"


@pytest.mark.asyncio
async def test_get_analysis_sections(async_client, test_analysis, db_session, override_get_db):
    """Test getting analysis sections"""
    # Add mock analysis result
    from core.models.database import AnalysisResult
    
    result = AnalysisResult(
        id=uuid4(),
        analysis_id=test_analysis.id,
        framework=FrameworkType.STRIDE,
        sections=[
            {
                "section_id": "threat_identification",
                "title": "Threat Identification",
                "status": "completed",
                "content": {"type": "table", "data": {}},
                "template_type": "table"
            }
        ],
        artifacts=[],
        duration=10.5,
        token_usage={"total_tokens": 1000}
    )
    
    db_session.add(result)
    await db_session.commit()
    
    response = await async_client.get(f"/api/analysis/{test_analysis.id}/sections")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    assert data[0]["framework"] == "STRIDE"
    assert data[0]["section_id"] == "threat_identification"
    assert data[0]["status"] == "completed"


@pytest.mark.asyncio
async def test_get_analysis_sections_by_framework(async_client, test_analysis, override_get_db):
    """Test getting sections filtered by framework"""
    response = await async_client.get(
        f"/api/analysis/{test_analysis.id}/sections",
        params={"framework": "STRIDE"}
    )
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_update_analysis(async_client, test_analysis, override_get_db):
    """Test updating analysis parameters"""
    update_data = {
        "system_description": "Updated system description",
        "frameworks": ["STRIDE", "PASTA"]
    }
    
    response = await async_client.patch(
        f"/api/analysis/{test_analysis.id}",
        json=update_data
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Analysis updated"


@pytest.mark.asyncio
async def test_update_analysis_not_pending(async_client, test_analysis, db_session, override_get_db):
    """Test updating non-pending analysis fails"""
    # Change status to in_progress
    test_analysis.status = AnalysisStatus.IN_PROGRESS
    await db_session.commit()
    
    update_data = {"system_description": "Updated description"}
    
    response = await async_client.patch(
        f"/api/analysis/{test_analysis.id}",
        json=update_data
    )
    
    assert response.status_code == 400
    assert "only update pending" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_cancel_analysis(async_client, test_analysis, override_get_db):
    """Test canceling an analysis"""
    with patch('api.analysis.manager.broadcast_analysis_update') as mock_broadcast:
        mock_broadcast.return_value = AsyncMock()
        
        response = await async_client.delete(f"/api/analysis/{test_analysis.id}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Analysis cancelled"


@pytest.mark.asyncio
async def test_cancel_completed_analysis(async_client, test_analysis, db_session, override_get_db):
    """Test canceling completed analysis fails"""
    # Change status to completed
    test_analysis.status = AnalysisStatus.COMPLETED
    await db_session.commit()
    
    response = await async_client.delete(f"/api/analysis/{test_analysis.id}")
    
    assert response.status_code == 400
    assert "only cancel pending or in-progress" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_analysis_context(async_client, test_analysis, override_get_db):
    """Test getting analysis context status"""
    with patch('core.context.manager.context_manager.get_context_stats') as mock_stats:
        mock_stats.return_value = {
            "status": "active",
            "total_documents": 5,
            "document_types": {
                "system_description": 1,
                "analysis_result": 3,
                "chat_message": 1
            }
        }
        
        response = await async_client.get(f"/api/analysis/{test_analysis.id}/context")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["analysis_id"] == str(test_analysis.id)
    assert data["context_status"]["status"] == "active"
    assert data["context_status"]["total_documents"] == 5


@pytest.mark.asyncio
async def test_export_analysis_not_implemented(async_client, test_analysis, override_get_db):
    """Test export endpoint returns not implemented"""
    response = await async_client.get(f"/api/analysis/{test_analysis.id}/export")
    
    assert response.status_code == 501
    assert "not yet implemented" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_analysis_with_section_ids(async_client, test_project, override_get_db):
    """Test creating analysis with specific section IDs"""
    request_data = {
        "project_id": str(test_project.id),
        "system_description": "Test system",
        "frameworks": ["STRIDE"],
        "section_ids": {
            "STRIDE": ["threat_identification", "mitigations"]
        }
    }
    
    with patch('api.analysis.run_analysis_task') as mock_task:
        response = await async_client.post("/api/analysis/", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_run_analysis_task_success(db_session, test_analysis):
    """Test run_analysis_task function"""
    from api.analysis import run_analysis_task
    from core.models.schemas import AgentContext
    
    context = AgentContext(
        analysis_id=test_analysis.id,
        project_id=test_analysis.project_id,
        system_description=test_analysis.system_description,
        artifacts={},
        metadata={}
    )
    
    with patch('api.analysis.AGENT_REGISTRY') as mock_registry:
        mock_agent = AsyncMock()
        mock_agent.analyze.return_value = AsyncMock(
            framework=FrameworkType.STRIDE,
            sections=[],
            artifacts=[],
            duration=1.0,
            token_usage={"total_tokens": 100}
        )
        
        mock_registry.get.return_value = lambda: mock_agent
        
        await run_analysis_task(
            str(test_analysis.id),
            context,
            [FrameworkType.STRIDE],
            None,
            db_session
        )
        
        mock_agent.analyze.assert_called_once()


@pytest.mark.asyncio
async def test_run_analysis_task_agent_error(db_session, test_analysis):
    """Test run_analysis_task with agent error"""
    from api.analysis import run_analysis_task
    from core.models.schemas import AgentContext
    
    context = AgentContext(
        analysis_id=test_analysis.id,
        project_id=test_analysis.project_id,
        system_description=test_analysis.system_description,
        artifacts={},
        metadata={}
    )
    
    with patch('api.analysis.AGENT_REGISTRY') as mock_registry:
        mock_agent = AsyncMock()
        mock_agent.analyze.side_effect = Exception("Agent error")
        
        mock_registry.get.return_value = lambda: mock_agent
        
        await run_analysis_task(
            str(test_analysis.id),
            context,
            [FrameworkType.STRIDE],
            None,
            db_session
        )
        
        # Analysis should still complete even if one agent fails
        await db_session.refresh(test_analysis)
        assert test_analysis.status == AnalysisStatus.COMPLETED