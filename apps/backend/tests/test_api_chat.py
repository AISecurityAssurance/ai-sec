"""
Tests for chat API endpoints
"""
import pytest
from unittest.mock import patch, AsyncMock
from uuid import uuid4
import json


@pytest.mark.asyncio
async def test_create_chat_message(async_client, test_analysis, override_get_db):
    """Test creating a chat message"""
    request_data = {
        "message": "What are the main security risks?",
        "analysis_id": str(test_analysis.id)
    }
    
    with patch('core.utils.llm_client.llm_manager.generate') as mock_generate:
        mock_generate.return_value = AsyncMock(
            content="The main security risks are...",
            model="gpt-4",
            usage={"total_tokens": 100}
        )
        
        response = await async_client.post("/api/chat/", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == request_data["message"]
    assert data["response"] == "The main security risks are..."
    assert data["analysis_id"] == str(test_analysis.id)
    assert "timestamp" in data
    assert data["metadata"]["model"] == "gpt-4"


@pytest.mark.asyncio
async def test_create_chat_message_without_analysis(async_client, override_get_db):
    """Test creating a chat message without analysis context"""
    request_data = {
        "message": "What is STRIDE?",
        "analysis_id": None
    }
    
    with patch('core.utils.llm_client.llm_manager.generate') as mock_generate:
        mock_generate.return_value = AsyncMock(
            content="STRIDE is a threat modeling framework...",
            model="gpt-4",
            usage={"total_tokens": 80}
        )
        
        response = await async_client.post("/api/chat/", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["message"] == request_data["message"]
    assert "STRIDE" in data["response"]
    assert data["analysis_id"] is None


@pytest.mark.asyncio
async def test_create_chat_message_with_context_manager(async_client, test_analysis, override_get_db):
    """Test chat message with context manager integration"""
    request_data = {
        "message": "Tell me about the authentication risks",
        "analysis_id": str(test_analysis.id)
    }
    
    with patch('core.utils.llm_client.llm_manager.generate') as mock_generate:
        mock_generate.return_value = AsyncMock(
            content="Authentication risks include...",
            model="gpt-4",
            usage={"total_tokens": 150}
        )
        
        with patch('core.context.manager.context_manager.get_relevant_context') as mock_context:
            mock_context.return_value = [
                {
                    "content": "Previous authentication analysis",
                    "metadata": {"type": "analysis_result", "framework": "STRIDE"},
                    "score": 0.9
                }
            ]
            
            with patch('core.context.manager.context_manager.add_chat_message') as mock_add:
                mock_add.return_value = AsyncMock()
                
                response = await async_client.post("/api/chat/", json=request_data)
    
    assert response.status_code == 200
    assert mock_context.called
    assert mock_add.call_count == 2  # User message and assistant response


@pytest.mark.asyncio
async def test_get_chat_history(async_client, test_analysis, db_session, override_get_db):
    """Test getting chat history"""
    # Create test chat messages
    from core.models.database import ChatMessage
    
    messages = []
    for i in range(3):
        msg = ChatMessage(
            id=uuid4(),
            analysis_id=test_analysis.id,
            message=f"Question {i}",
            response=f"Answer {i}",
            metadata={"model": "gpt-4"}
        )
        messages.append(msg)
        db_session.add(msg)
    
    await db_session.commit()
    
    response = await async_client.get(
        "/api/chat/history",
        params={"analysis_id": str(test_analysis.id)}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 3
    assert len(data["messages"]) == 3
    assert data["messages"][0]["message"] == "Question 2"  # Ordered by created_at desc


@pytest.mark.asyncio
async def test_get_chat_history_with_pagination(async_client, override_get_db):
    """Test chat history pagination"""
    response = await async_client.get(
        "/api/chat/history",
        params={"limit": 10, "offset": 5}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "messages" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_chat_message(async_client, db_session, override_get_db):
    """Test getting specific chat message"""
    # Create test message
    from core.models.database import ChatMessage
    
    message = ChatMessage(
        id=uuid4(),
        analysis_id=None,
        message="Test question",
        response="Test answer",
        metadata={"model": "gpt-4", "tokens": 50}
    )
    db_session.add(message)
    await db_session.commit()
    
    response = await async_client.get(f"/api/chat/{message.id}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == str(message.id)
    assert data["message"] == "Test question"
    assert data["response"] == "Test answer"
    assert data["metadata"]["tokens"] == 50


@pytest.mark.asyncio
async def test_get_chat_message_not_found(async_client, override_get_db):
    """Test getting non-existent chat message"""
    fake_id = uuid4()
    response = await async_client.get(f"/api/chat/{fake_id}")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Message not found"


@pytest.mark.asyncio
async def test_delete_chat_message(async_client, db_session, override_get_db):
    """Test deleting chat message"""
    # Create test message
    from core.models.database import ChatMessage
    
    message = ChatMessage(
        id=uuid4(),
        analysis_id=None,
        message="Delete me",
        response="I will be deleted",
        metadata={}
    )
    db_session.add(message)
    await db_session.commit()
    
    response = await async_client.delete(f"/api/chat/{message.id}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Chat message deleted"
    
    # Verify deletion
    deleted = await db_session.get(ChatMessage, message.id)
    assert deleted is None


@pytest.mark.asyncio
async def test_get_chat_suggestions(async_client, test_analysis, override_get_db):
    """Test getting chat suggestions"""
    with patch('core.utils.llm_client.llm_manager.generate') as mock_generate:
        mock_generate.return_value = AsyncMock(
            content=json.dumps([
                "What are the critical threats?",
                "How do we mitigate the risks?",
                "Which controls should we implement first?",
                "What is the overall risk level?",
                "Are there any compliance concerns?"
            ]),
            model="gpt-4",
            usage={"total_tokens": 100}
        )
        
        response = await async_client.post(
            "/api/chat/suggestions",
            json={"analysis_id": str(test_analysis.id)}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "suggestions" in data
    assert len(data["suggestions"]) == 5
    assert "critical threats" in data["suggestions"][0]


@pytest.mark.asyncio
async def test_get_chat_suggestions_parse_error(async_client, test_analysis, override_get_db):
    """Test chat suggestions with parse error fallback"""
    with patch('core.utils.llm_client.llm_manager.generate') as mock_generate:
        mock_generate.return_value = AsyncMock(
            content="Invalid JSON response",
            model="gpt-4",
            usage={"total_tokens": 50}
        )
        
        response = await async_client.post(
            "/api/chat/suggestions",
            json={"analysis_id": str(test_analysis.id)}
        )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should return default suggestions
    assert "suggestions" in data
    assert len(data["suggestions"]) == 5
    assert "main security risks" in data["suggestions"][0]


@pytest.mark.asyncio
async def test_create_chat_llm_error(async_client, test_analysis, override_get_db):
    """Test chat message creation with LLM error"""
    request_data = {
        "message": "Test question",
        "analysis_id": str(test_analysis.id)
    }
    
    with patch('core.utils.llm_client.llm_manager.generate') as mock_generate:
        mock_generate.side_effect = Exception("LLM service unavailable")
        
        response = await async_client.post("/api/chat/", json=request_data)
    
    assert response.status_code == 500
    assert "Failed to generate response" in response.json()["detail"]


@pytest.mark.asyncio
async def test_build_chat_context(test_analysis, db_session):
    """Test build_chat_context function"""
    from api.chat import build_chat_context
    
    # Add analysis result
    from core.models.database import AnalysisResult
    from core.models.schemas import FrameworkType
    
    result = AnalysisResult(
        id=uuid4(),
        analysis_id=test_analysis.id,
        framework=FrameworkType.STRIDE,
        sections=[
            {
                "title": "Threat Identification",
                "status": "completed"
            }
        ],
        artifacts=[],
        duration=10.0,
        token_usage={"total_tokens": 500}
    )
    db_session.add(result)
    await db_session.commit()
    
    context = await build_chat_context(test_analysis.id, db_session, "test question")
    
    assert "System Description:" in context
    assert test_analysis.system_description in context