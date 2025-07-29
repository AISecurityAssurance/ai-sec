# Proposed backend structure


apps/backend/
├── core/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                    # Base agent class
│   │   ├── orchestrator.py            # SA orchestrator agent
│   │   ├── framework_agents/
│   │   │   ├── __init__.py
│   │   │   ├── stpa_sec.py
│   │   │   ├── stride.py
│   │   │   ├── pasta.py
│   │   │   ├── dread.py
│   │   │   ├── maestro.py
│   │   │   ├── linddun.py
│   │   │   ├── hazop.py
│   │   │   └── octave.py
│   │   └── specialized/
│   │       ├── __init__.py
│   │       ├── categorizer.py         # System categorization
│   │       ├── integrator.py          # Cross-framework integration
│   │       ├── suggester.py           # Plugin suggestion agent
│   │       └── mcp_adapter.py         # MCP plugin adapter
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── context_manager.py         # Context window management
│   │   ├── artifact_store.py          # Artifact storage
│   │   └── indexer.py                 # LlamaIndex integration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── analysis.py                # SQLAlchemy models
│   │   ├── schemas.py                 # Pydantic schemas
│   │   └── templates.py               # Template data models
│   ├── prompts/                       # Keep existing prompts
│   │   └── (existing structure)
│   ├── templates/
│   │   ├── __init__.py
│   │   ├── mapper.py                  # Template mapping system
│   │   └── validators.py              # Template validation
│   └── utils/
│       ├── __init__.py
│       ├── llm_client.py              # LLM abstraction
│       └── prompt_manager.py          # Prompt management
├── api/
│   ├── __init__.py
│   ├── main.py                        # FastAPI app
│   ├── dependencies.py                # Dependency injection
│   ├── websocket.py                   # WebSocket manager
│   └── routes/
│       ├── __init__.py
│       ├── analysis.py                # Analysis endpoints
│       ├── artifacts.py               # Artifact management
│       ├── chat.py                    # SA chat endpoints
│       └── versions.py                # Version control
├── storage/
│   ├── __init__.py
│   ├── database.py                    # Database setup
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── analysis.py                # Analysis repository
│   │   └── artifacts.py               # Artifact repository
│   └── graph.py                       # Neo4j integration
├── config/
│   ├── __init__.py
│   └── settings.py                    # Configuration
├── tests/
│   └── (test structure)
├── alembic/                           # Database migrations
│   └── versions/
├── .env.example
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── makefile

# TODOs
Use uv package manager with makefile and pyproject.toml to set up the environment. 



Instructions for Claude Code
Project Setup

Initial Setup
bashcd apps/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with API keys

# Initialize database
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

Docker Setup
bash# Start services
docker-compose up -d

# This starts:
# - PostgreSQL
# - Redis
# - Neo4j


Implementation Order

Week 1 - Core Infrastructure

Set up models and schemas
Implement base agent class
Create template mapper
Set up FastAPI with basic endpoints
Implement WebSocket manager


Week 2 - Agent Implementation

Implement STPA-Sec agent (priority - others depend on it)
Implement STRIDE agent
Create orchestrator agent
Add context manager with LlamaIndex


Week 3 - Advanced Features

Implement remaining framework agents
Add plugin suggester
Create integration agents
Implement versioning system


Week 4 - Polish & Integration

Add MCP adapter
Optimize context window management
Add comprehensive error handling
Create extensive tests



Key Implementation Notes

Template Alignment

Every agent output MUST map to frontend templates
Use the TemplateMapper for all outputs
Test outputs against frontend expectations


Context Management

STPA-Sec runs first and provides system structure
Other agents use STPA-Sec results as context
Use LlamaIndex for efficient retrieval


Real-time Updates

Send WebSocket updates for each analysis stage
Include partial results when possible
Handle connection drops gracefully


Error Handling

Graceful degradation if an agent fails
Continue with other analyses
Report errors clearly to frontend


Performance

Use async throughout
Implement caching for repeated queries
Batch LLM calls when possible



Testing Strategy

Unit Tests

Test each agent independently
Mock LLM responses for consistency
Test template mapping


Integration Tests

Test full analysis pipeline
Test WebSocket updates
Test context management


Load Tests

Test concurrent analyses
Test large system descriptions
Test context window limits



This structure provides a solid foundation for the Security Analyst backend that integrates seamlessly with your frontend template system. The hybrid approach gives you the flexibility to use the best tools for each component while maintaining control over the core functionality.