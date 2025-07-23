"""
Tests for context manager with LlamaIndex
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from uuid import uuid4
from datetime import datetime
import json

from core.context.manager import ContextManager
from core.models.schemas import ChatMessage


@pytest.fixture
def context_manager():
    """Create context manager instance"""
    with patch('core.context.manager.ContextManager._initialize_embedding') as mock_embed:
        mock_embed.return_value = MagicMock()
        return ContextManager()


@pytest.fixture
def analysis_id():
    """Create test analysis ID"""
    return uuid4()


@pytest.mark.asyncio
async def test_initialize_analysis_context(context_manager, analysis_id):
    """Test initializing analysis context"""
    system_description = "Test banking system with authentication"
    
    context = await context_manager.initialize_analysis_context(
        analysis_id,
        system_description,
        existing_artifacts={"previous": {"data": "test"}}
    )
    
    assert context.analysis_id == analysis_id
    assert context.system_description == system_description
    assert "previous" in context.artifacts
    assert str(analysis_id) in context_manager.indices
    assert str(analysis_id) in context_manager.storage_contexts


@pytest.mark.asyncio
async def test_add_analysis_result(context_manager, analysis_id):
    """Test adding analysis result to context"""
    # Initialize context first
    await context_manager.initialize_analysis_context(
        analysis_id, "Test system", None
    )
    
    result = {
        "framework": "STRIDE",
        "threats": ["Spoofing", "Tampering"],
        "risk_level": "High"
    }
    
    # Mock the index insert method
    mock_index = MagicMock()
    mock_index.insert = MagicMock()
    context_manager.indices[str(analysis_id)] = mock_index
    
    await context_manager.add_analysis_result(
        analysis_id,
        "STRIDE",
        result
    )
    
    # Verify document was inserted
    mock_index.insert.assert_called_once()
    inserted_doc = mock_index.insert.call_args[0][0]
    assert json.loads(inserted_doc.text) == result
    assert inserted_doc.metadata["framework"] == "STRIDE"
    assert inserted_doc.metadata["type"] == "analysis_result"


@pytest.mark.asyncio
async def test_add_chat_message(context_manager, analysis_id):
    """Test adding chat message to context"""
    # Initialize context first
    await context_manager.initialize_analysis_context(
        analysis_id, "Test system", None
    )
    
    message = ChatMessage(
        role="user",
        content="What are the main risks?",
        timestamp=datetime.utcnow()
    )
    
    # Mock the index insert method
    mock_index = MagicMock()
    mock_index.insert = MagicMock()
    context_manager.indices[str(analysis_id)] = mock_index
    
    await context_manager.add_chat_message(analysis_id, message)
    
    # Verify document was inserted
    mock_index.insert.assert_called_once()
    inserted_doc = mock_index.insert.call_args[0][0]
    assert inserted_doc.text == message.content
    assert inserted_doc.metadata["role"] == "user"
    assert inserted_doc.metadata["type"] == "chat_message"


@pytest.mark.asyncio
async def test_get_relevant_context(context_manager, analysis_id):
    """Test retrieving relevant context"""
    # Initialize context first
    await context_manager.initialize_analysis_context(
        analysis_id, "Test system", None
    )
    
    # Mock retriever and nodes
    mock_node = MagicMock()
    mock_node.node.text = "Relevant content"
    mock_node.node.metadata = {"type": "analysis_result", "framework": "STRIDE"}
    mock_node.score = 0.95
    
    with patch('llama_index.core.retrievers.VectorIndexRetriever') as mock_retriever_class:
        mock_retriever = MagicMock()
        mock_retriever.retrieve.return_value = [mock_node]
        mock_retriever_class.return_value = mock_retriever
        
        context_items = await context_manager.get_relevant_context(
            analysis_id,
            "security threats",
            top_k=5
        )
    
    assert len(context_items) == 1
    assert context_items[0]["content"] == "Relevant content"
    assert context_items[0]["metadata"]["framework"] == "STRIDE"
    assert context_items[0]["score"] == 0.95


@pytest.mark.asyncio
async def test_get_conversation_history(context_manager, analysis_id):
    """Test retrieving conversation history"""
    # Initialize context first
    await context_manager.initialize_analysis_context(
        analysis_id, "Test system", None
    )
    
    # Mock get_relevant_context to return chat messages
    mock_messages = [
        {
            "content": "Hello",
            "metadata": {
                "role": "user",
                "timestamp": "2024-01-01T10:00:00"
            }
        },
        {
            "content": "Hi there!",
            "metadata": {
                "role": "assistant",
                "timestamp": "2024-01-01T10:01:00"
            }
        }
    ]
    
    with patch.object(context_manager, 'get_relevant_context') as mock_get:
        mock_get.return_value = mock_messages
        
        history = await context_manager.get_conversation_history(
            analysis_id,
            limit=10
        )
    
    assert len(history) == 2
    assert history[0].role == "user"
    assert history[0].content == "Hello"
    assert history[1].role == "assistant"


@pytest.mark.asyncio
async def test_get_analysis_artifacts(context_manager, analysis_id):
    """Test retrieving analysis artifacts"""
    # Initialize context first
    await context_manager.initialize_analysis_context(
        analysis_id, "Test system", None
    )
    
    # Mock artifacts
    mock_artifacts = [
        {
            "content": json.dumps({"threats": ["S1", "T1"]}),
            "metadata": {"type": "artifact_stride_threats"}
        },
        {
            "content": json.dumps({"diagram": "DFD data"}),
            "metadata": {"type": "artifact_dfd"}
        }
    ]
    
    with patch.object(context_manager, 'get_relevant_context') as mock_get:
        mock_get.return_value = mock_artifacts
        
        artifacts = await context_manager.get_analysis_artifacts(
            analysis_id,
            framework="STRIDE"
        )
    
    assert "stride_threats" in artifacts
    assert artifacts["stride_threats"]["threats"] == ["S1", "T1"]
    assert "dfd" in artifacts


@pytest.mark.asyncio
async def test_synthesize_context_summary(context_manager, analysis_id):
    """Test synthesizing context summary"""
    # Initialize context first
    await context_manager.initialize_analysis_context(
        analysis_id, "Test system", None
    )
    
    # Mock query engine
    mock_response = MagicMock()
    mock_response.__str__ = lambda self: "Summary of security analysis"
    
    mock_query_engine = MagicMock()
    mock_query_engine.query = MagicMock(return_value=mock_response)
    
    mock_index = MagicMock()
    mock_index.as_query_engine = MagicMock(return_value=mock_query_engine)
    
    context_manager.indices[str(analysis_id)] = mock_index
    
    summary = await context_manager.synthesize_context_summary(
        analysis_id,
        "What are the main findings?"
    )
    
    assert summary == "Summary of security analysis"
    mock_query_engine.query.assert_called_once()


@pytest.mark.asyncio
async def test_cleanup_analysis_context(context_manager, analysis_id):
    """Test cleaning up analysis context"""
    # Initialize context first
    await context_manager.initialize_analysis_context(
        analysis_id, "Test system", None
    )
    
    # Verify context exists
    assert str(analysis_id) in context_manager.indices
    assert str(analysis_id) in context_manager.storage_contexts
    
    # Clean up
    await context_manager.cleanup_analysis_context(analysis_id)
    
    # Verify cleanup
    assert str(analysis_id) not in context_manager.indices
    assert str(analysis_id) not in context_manager.storage_contexts


def test_get_context_stats(context_manager, analysis_id):
    """Test getting context statistics"""
    # No context case
    stats = context_manager.get_context_stats(analysis_id)
    assert stats["status"] == "no_context"
    
    # Mock active context
    mock_index = MagicMock()
    mock_storage = MagicMock()
    
    # Mock document store
    mock_docs = {
        "doc1": MagicMock(metadata={"type": "system_description"}),
        "doc2": MagicMock(metadata={"type": "analysis_result"}),
        "doc3": MagicMock(metadata={"type": "analysis_result"}),
        "doc4": MagicMock(metadata={"type": "chat_message"})
    }
    
    mock_storage.docstore.docs = mock_docs
    mock_storage.docstore.get_document = lambda doc_id: mock_docs[doc_id]
    
    context_manager.indices[str(analysis_id)] = mock_index
    context_manager.storage_contexts[str(analysis_id)] = mock_storage
    
    stats = context_manager.get_context_stats(analysis_id)
    
    assert stats["status"] == "active"
    assert stats["total_documents"] == 4
    assert stats["document_types"]["system_description"] == 1
    assert stats["document_types"]["analysis_result"] == 2
    assert stats["document_types"]["chat_message"] == 1


@pytest.mark.asyncio
async def test_context_manager_error_handling(context_manager, analysis_id):
    """Test error handling in context manager"""
    # Test adding result without initialized context
    await context_manager.add_analysis_result(
        analysis_id,
        "STRIDE",
        {"test": "data"}
    )
    # Should not raise exception
    
    # Test getting context without initialization
    items = await context_manager.get_relevant_context(
        analysis_id,
        "test query"
    )
    assert items == []
    
    # Test conversation history without initialization
    history = await context_manager.get_conversation_history(analysis_id)
    assert history == []


def test_initialize_embedding_openai(context_manager):
    """Test OpenAI embedding initialization"""
    with patch('config.settings.settings.EMBEDDING_MODEL', 'openai-text-embedding-3-small'):
        with patch('llama_index.embeddings.openai.OpenAIEmbedding') as mock_openai:
            context_manager._initialize_embedding()
            mock_openai.assert_called_once()


def test_initialize_embedding_huggingface(context_manager):
    """Test HuggingFace embedding initialization"""
    with patch('config.settings.settings.EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2'):
        with patch('llama_index.embeddings.huggingface.HuggingFaceEmbedding') as mock_hf:
            context_manager._initialize_embedding()
            mock_hf.assert_called_once()


def test_initialize_embedding_default(context_manager):
    """Test default embedding initialization"""
    with patch('config.settings.settings.EMBEDDING_MODEL', 'unknown-model'):
        with patch('llama_index.embeddings.huggingface.HuggingFaceEmbedding') as mock_hf:
            context_manager._initialize_embedding()
            # Should use default HuggingFace model
            mock_hf.assert_called_with(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )