"""
Tests for STRIDE agent
"""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from core.agents.framework_agents.stride import StrideAgent
from core.models.schemas import (
    FrameworkType, AnalysisStatus, AgentContext, AgentResult
)


@pytest.fixture
def stride_agent():
    """Create STRIDE agent instance"""
    return StrideAgent()


@pytest.fixture
def agent_context():
    """Create test agent context"""
    return AgentContext(
        analysis_id=uuid4(),
        project_id=uuid4(),
        system_description="""
        Online Banking System
        - User authentication service
        - Account management API
        - Payment processing engine
        - Database with customer data
        - External payment gateway integration
        """,
        artifacts={},
        metadata={}
    )


@pytest.mark.asyncio
async def test_stride_agent_initialization(stride_agent):
    """Test STRIDE agent initialization"""
    assert stride_agent.framework == FrameworkType.STRIDE
    assert len(stride_agent.get_sections()) == 8  # STRIDE has 8 sections


@pytest.mark.asyncio
async def test_stride_get_sections(stride_agent):
    """Test STRIDE sections definition"""
    sections = stride_agent.get_sections()
    section_ids = [s["id"] for s in sections]
    
    # Verify all STRIDE sections are present
    expected_sections = [
        "data_flow_diagram",
        "trust_boundaries", 
        "assets",
        "threat_identification",
        "threat_analysis",
        "risk_matrix",
        "mitigations",
        "residual_risks"
    ]
    
    for expected in expected_sections:
        assert expected in section_ids


@pytest.mark.asyncio
async def test_parse_dfd_response(stride_agent):
    """Test parsing of Data Flow Diagram response"""
    mock_response = """
    DATA FLOW DIAGRAM:
    
    Entity: User (External Entity)
    Entity: Web Application (Process)
    Entity: Authentication Service (Process)
    Entity: Database (Data Store)
    
    Flow: User -> Web Application: Login Request
    Flow: Web Application -> Authentication Service: Validate Credentials
    Flow: Authentication Service -> Database: Query User Data
    Flow: Database -> Authentication Service: User Details
    Flow: Authentication Service -> Web Application: Auth Token
    Flow: Web Application -> User: Session Cookie
    """
    
    result = await stride_agent._parse_response(mock_response, "data_flow_diagram")
    
    assert result["type"] == "diagram"
    assert len(result["data"]["nodes"]) >= 4
    assert len(result["data"]["edges"]) >= 6
    
    # Check node types
    node_types = [node["type"] for node in result["data"]["nodes"]]
    assert "external_entity" in node_types
    assert "process" in node_types
    assert "data_store" in node_types


@pytest.mark.asyncio
async def test_parse_threats_response(stride_agent):
    """Test parsing of threat identification response"""
    mock_response = """
    STRIDE THREAT ANALYSIS:
    
    S - SPOOFING:
    S1: User identity spoofing at login
    Component: Authentication Service
    Description: Attacker could impersonate legitimate user
    
    T - TAMPERING:
    T1: Transaction data modification
    Component: Payment Processing
    Description: Attacker modifies payment amounts in transit
    
    R - REPUDIATION:
    R1: User denies transaction
    Component: Transaction Logging
    Description: User claims they didn't authorize a payment
    
    I - INFORMATION DISCLOSURE:
    I1: Customer data exposure
    Component: Database
    Description: Unauthorized access to sensitive customer information
    
    D - DENIAL OF SERVICE:
    D1: Authentication service overload
    Component: Authentication Service
    Description: Flood login endpoint with requests
    
    E - ELEVATION OF PRIVILEGE:
    E1: Regular user gains admin access
    Component: Authorization Module
    Description: Privilege escalation through role manipulation
    """
    
    result = await stride_agent._parse_response(mock_response, "threat_identification")
    
    assert result["type"] == "table"
    assert "headers" in result["data"]
    assert "rows" in result["data"]
    
    # Should have threats for all 6 STRIDE categories
    threats = result["data"]["rows"]
    assert len(threats) >= 6
    
    # Check threat categories
    categories = [row[1] for row in threats]  # Category is second column
    for category in ["Spoofing", "Tampering", "Repudiation", 
                    "Information Disclosure", "Denial of Service", 
                    "Elevation of Privilege"]:
        assert any(category in cat for cat in categories)


@pytest.mark.asyncio
async def test_parse_mitigations_response(stride_agent):
    """Test parsing of mitigations response"""
    mock_response = """
    SECURITY CONTROLS AND MITIGATIONS:
    
    M1: Multi-Factor Authentication
    Threats Addressed: S1, E1
    Type: Preventive
    Description: Require MFA for all user logins
    Implementation: TOTP-based second factor
    Effectiveness: High
    
    M2: End-to-End Encryption
    Threats Addressed: T1, I1
    Type: Preventive
    Description: Encrypt all data in transit using TLS 1.3
    Implementation: Certificate pinning on mobile apps
    Effectiveness: High
    
    M3: Rate Limiting
    Threats Addressed: D1
    Type: Preventive
    Description: Implement aggressive rate limits on auth endpoints
    Implementation: Redis-based rate limiter with exponential backoff
    Effectiveness: Medium
    """
    
    result = await stride_agent._parse_response(mock_response, "mitigations")
    
    assert result["type"] == "table"
    mitigations = result["data"]["rows"]
    assert len(mitigations) >= 3
    
    # Check mitigation structure
    for mitigation in mitigations:
        assert len(mitigation) >= 5  # ID, Control, Type, Threats, Description, Effectiveness


@pytest.mark.asyncio
async def test_parse_risk_matrix_response(stride_agent):
    """Test risk matrix generation"""
    mock_response = """
    THREAT ANALYSIS:
    T1: High likelihood, High impact - Authentication bypass
    T2: Medium likelihood, Critical impact - Data breach
    T3: Low likelihood, Medium impact - Service disruption
    T4: High likelihood, Low impact - Log tampering
    """
    
    result = await stride_agent._parse_response(mock_response, "risk_matrix")
    
    assert result["type"] == "heat_map"
    assert "data" in result["data"]
    assert "x_labels" in result["data"]
    assert "y_labels" in result["data"]
    assert result["data"]["title"] == "STRIDE Risk Matrix"


@pytest.mark.asyncio
async def test_full_analysis(stride_agent, agent_context):
    """Test full STRIDE analysis"""
    with patch('core.utils.llm_client.llm_manager.generate') as mock_generate:
        mock_generate.return_value = AsyncMock(
            content="Mock analysis response",
            model="gpt-4",
            usage={"total_tokens": 500}
        )
        
        result = await stride_agent.analyze(
            agent_context,
            section_ids=["threat_identification"]
        )
        
        assert isinstance(result, AgentResult)
        assert result.framework == FrameworkType.STRIDE
        assert len(result.sections) == 1
        assert result.sections[0]["section_id"] == "threat_identification"


@pytest.mark.asyncio
async def test_extract_artifacts(stride_agent, agent_context):
    """Test artifact extraction"""
    # Create mock section results
    from core.agents.base import SectionResult
    
    sections = [
        SectionResult(
            section_id="data_flow_diagram",
            title="Data Flow Diagram",
            content={"type": "diagram", "data": {"nodes": [], "edges": []}},
            template_type="diagram",
            status=AnalysisStatus.COMPLETED
        ),
        SectionResult(
            section_id="threat_identification",
            title="Threat Identification",
            content={"type": "table", "data": {"headers": [], "rows": []}},
            template_type="table",
            status=AnalysisStatus.COMPLETED
        )
    ]
    
    artifacts = stride_agent._extract_artifacts(sections)
    
    assert len(artifacts) == 2
    assert artifacts[0]["type"] == "data_flow_diagram"
    assert artifacts[0]["name"] == "STRIDE Data Flow Diagram"
    assert artifacts[1]["type"] == "stride_threats"
    assert artifacts[1]["name"] == "STRIDE Threat Analysis"