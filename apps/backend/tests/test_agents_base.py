"""
Tests for base agent functionality
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from uuid import uuid4

from core.agents.base import BaseAnalysisAgent, SectionResult
from core.models.schemas import (
    FrameworkType, AnalysisStatus, AgentContext, AgentResult
)


class TestAgent(BaseAnalysisAgent):
    """Test implementation of base agent"""
    
    def __init__(self):
        super().__init__(FrameworkType.STPA_SEC)
    
    async def analyze(self, context: AgentContext, section_ids=None):
        """Test analyze method"""
        sections = await self.analyze_sections(context, section_ids)
        return AgentResult(
            framework=self.framework,
            sections=[s.model_dump() for s in sections],
            artifacts=[],
            duration=1.0,
            token_usage={"total_tokens": 100}
        )
    
    def get_sections(self):
        """Test sections"""
        return [
            {"id": "test_section", "title": "Test Section", "template": "table"},
            {"id": "another_section", "title": "Another Section", "template": "text"}
        ]
    
    async def _parse_response(self, response: str, section_id: str):
        """Test parse response"""
        if section_id == "test_section":
            return {
                "type": "table",
                "data": {
                    "headers": ["Column 1", "Column 2"],
                    "rows": [["Value 1", "Value 2"]]
                }
            }
        else:
            return {
                "type": "text",
                "content": response,
                "format": "markdown"
            }


@pytest.fixture
def test_agent():
    """Create test agent instance"""
    return TestAgent()


@pytest.fixture
def agent_context():
    """Create test agent context"""
    return AgentContext(
        analysis_id=uuid4(),
        project_id=uuid4(),
        system_description="Test system description",
        artifacts={},
        metadata={}
    )


@pytest.mark.asyncio
async def test_agent_initialization(test_agent):
    """Test agent initialization"""
    assert test_agent.framework == FrameworkType.STPA_SEC
    assert test_agent.prompt_dir.name == "stpa-sec"


@pytest.mark.asyncio
async def test_get_sections(test_agent):
    """Test get_sections method"""
    sections = test_agent.get_sections()
    assert len(sections) == 2
    assert sections[0]["id"] == "test_section"
    assert sections[0]["template"] == "table"


@pytest.mark.asyncio
async def test_analyze_section(test_agent, agent_context):
    """Test analyze_section method"""
    with patch('core.utils.llm_client.llm_manager.generate') as mock_generate:
        mock_generate.return_value = AsyncMock(
            content="Test response content",
            model="gpt-4",
            usage={"total_tokens": 50}
        )
        
        # Mock the _load_prompt method
        test_agent._load_prompt = AsyncMock(return_value="Test prompt")
        
        result = await test_agent.analyze_section("test_section", agent_context)
        
        assert isinstance(result, SectionResult)
        assert result.section_id == "test_section"
        assert result.title == "Test Section"
        assert result.template_type == "table"
        assert result.status == AnalysisStatus.COMPLETED
        assert result.content["type"] == "table"


@pytest.mark.asyncio
async def test_analyze_sections_with_notifier(test_agent, agent_context):
    """Test analyze_sections with WebSocket notifier"""
    # Create mock notifier
    notifier = AsyncMock()
    notifier.notify_section_start = AsyncMock()
    notifier.notify_section_complete = AsyncMock()
    notifier.notify_analysis_progress = AsyncMock()
    
    with patch('core.utils.llm_client.llm_manager.generate') as mock_generate:
        mock_generate.return_value = AsyncMock(
            content="Test response",
            model="gpt-4",
            usage={"total_tokens": 50}
        )
        
        test_agent._load_prompt = AsyncMock(return_value="Test prompt")
        
        results = await test_agent.analyze_sections(
            agent_context, 
            section_ids=["test_section"],
            notifier=notifier
        )
        
        assert len(results) == 1
        assert notifier.notify_section_start.called
        assert notifier.notify_section_complete.called
        assert notifier.notify_analysis_progress.called


@pytest.mark.asyncio
async def test_analyze_section_error(test_agent, agent_context):
    """Test analyze_section error handling"""
    with patch('core.utils.llm_client.llm_manager.generate') as mock_generate:
        mock_generate.side_effect = Exception("LLM error")
        
        test_agent._load_prompt = AsyncMock(return_value="Test prompt")
        
        results = await test_agent.analyze_sections(agent_context, ["test_section"])
        
        assert len(results) == 1
        assert results[0].status == AnalysisStatus.FAILED
        assert results[0].error == "LLM error"


@pytest.mark.asyncio
async def test_build_prompt_with_context(test_agent, agent_context):
    """Test _build_prompt with context manager integration"""
    with patch('core.context.manager.context_manager.get_relevant_context') as mock_context:
        mock_context.return_value = [
            {
                "content": "Previous analysis content",
                "metadata": {"framework": "STRIDE", "type": "artifact"},
                "score": 0.9
            }
        ]
        
        with patch('core.context.manager.context_manager.get_conversation_history') as mock_history:
            mock_history.return_value = []
            
            prompt = await test_agent._build_prompt(
                "Base prompt {{SYSTEM_DESCRIPTION}}", 
                agent_context,
                "test_section"
            )
            
            assert "Test system description" in prompt
            assert "Previous analysis content" in prompt
            assert "From STRIDE:" in prompt


def test_get_section_title(test_agent):
    """Test _get_section_title method"""
    title = test_agent._get_section_title("test_section")
    assert title == "Test Section"
    
    # Test unknown section
    title = test_agent._get_section_title("unknown_section")
    assert title == "Unknown Section"


def test_get_template_type(test_agent):
    """Test _get_template_type method"""
    template = test_agent._get_template_type("test_section")
    assert template == "table"
    
    # Test unknown section
    template = test_agent._get_template_type("unknown_section")
    assert template == "text"


def test_create_table(test_agent):
    """Test create_table helper method"""
    table = test_agent.create_table(
        columns=[{"key": "col1", "label": "Column 1"}],
        rows=[{"col1": "Value 1"}]
    )
    
    assert table["type"] == "table"
    assert "data" in table
    assert table["data"]["columns"] == [{"key": "col1", "label": "Column 1"}]


def test_create_chart(test_agent):
    """Test create_chart helper method"""
    chart = test_agent.create_chart(
        chart_type="bar",
        labels=["Label 1", "Label 2"],
        datasets=[{"label": "Dataset 1", "data": [10, 20]}]
    )
    
    assert chart["type"] == "chart"
    assert chart["data"]["type"] == "bar"
    assert chart["data"]["labels"] == ["Label 1", "Label 2"]


def test_create_diagram(test_agent):
    """Test create_diagram helper method"""
    diagram = test_agent.create_diagram(
        nodes=[{"id": "1", "label": "Node 1"}],
        edges=[{"source": "1", "target": "2"}]
    )
    
    assert diagram["type"] == "diagram"
    assert len(diagram["data"]["nodes"]) == 1
    assert len(diagram["data"]["edges"]) == 1


def test_create_text(test_agent):
    """Test create_text helper method"""
    text = test_agent.create_text("Test content", "markdown")
    
    assert text["type"] == "text"
    assert text["content"] == "Test content"
    assert text["format"] == "markdown"


def test_create_list(test_agent):
    """Test create_list helper method"""
    list_content = test_agent.create_list(
        items=[{"text": "Item 1"}, {"text": "Item 2"}],
        ordered=True
    )
    
    assert list_content["type"] == "list"
    assert list_content["ordered"] is True
    assert len(list_content["items"]) == 2