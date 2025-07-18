# Security Analysis Platform - Architecture & Implementation Plan

## Executive Summary

A comprehensive Systems Security Engineering Platform that provides interactive, AI-powered security analysis for various system types. The platform uses a coordinating agent to orchestrate specialized analysis agents, allowing users to perform deep security analysis through a self-service interface.

## Core Concept

**Self-Service Model with Agent Orchestration**
- Users interact with a conversational coordinating agent
- The coordinator manages specialized agents (STPA-Sec, STRIDE, Code Analysis, etc.)
- Each specialized agent handles specific analysis tasks
- Results are integrated and presented through an interactive interface

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   User Interface Layer                   │
│         (Web UI with conversational interface)           │
└─────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│              Orchestration Layer                         │
│         Coordinating Agent (Orchestrator)                │
│  • User interaction management                           │
│  • Task delegation to specialized agents                 │
│  • Result synthesis and presentation                     │
└─────────────────────────────────────────────────────────┘
                              │
┌──────────────┬──────────────┬─────────────┬────────────┐
│ STPA-Sec     │ STRIDE       │ Code        │ CVE Search │
│ Agent        │ Agent        │ Analysis    │ Agent      │
│              │              │ Agent       │            │
└──────────────┴──────────────┴─────────────┴────────────┘
                              │
┌─────────────────────────────────────────────────────────┐
│                  Core Services Layer                     │
│ • Storage Abstraction  • Model Provider Interface       │
│ • Graph Database       • Document Management            │
│ • Plugin System        • Configuration Management       │
└─────────────────────────────────────────────────────────┘
```

## Deployment Models

### 1. Local-First Hybrid Approach

**Default Mode: Completely Local**
- Runs on developer/user machine
- Uses local models (Ollama)
- Stores data locally
- No external dependencies
- Zero ongoing costs

**Cloud-Enhanced Mode (Optional)**
- Can use cloud model APIs (Claude, GPT-4, etc.)
- Optional cloud storage
- Enhanced collaboration features
- Pay-per-use model

### Implementation Strategy

```yaml
# deployment/config.yaml
deployment:
  mode: "local"  # local | hybrid | cloud
  
  local:
    storage: "./data"
    models:
      provider: "ollama"
      default: "llama3"
  
  hybrid:
    storage: 
      primary: "./data"
      backup: "s3://bucket" # optional
    models:
      providers: ["ollama", "openai", "anthropic"]
      
  cloud:
    storage: "s3://bucket"
    models:
      providers: ["openai", "anthropic", "google"]
```

## Security Model

### Storage Abstraction Layer

```python
# core/storage/base.py
from typing import Protocol, Optional

class StorageProvider(Protocol):
    """Abstract storage interface for deployment flexibility"""
    
    async def store(self, key: str, data: bytes, 
                   encrypted: bool = False) -> None:
        """Store data with optional encryption"""
        ...
    
    async def retrieve(self, key: str) -> Optional[bytes]:
        """Retrieve stored data"""
        ...
    
    async def list(self, prefix: str) -> List[str]:
        """List keys with given prefix"""
        ...
    
    async def delete(self, key: str) -> None:
        """Delete stored data"""
        ...
```

### Security Levels

1. **Air-Gapped** (Highest Security)
   - No network connections
   - Local models only
   - Encrypted local storage
   - For classified/sensitive environments

2. **Restricted** (High Security)
   - Local storage only
   - External model APIs allowed
   - For proprietary/confidential data

3. **Hybrid** (Flexible Security)
   - User chooses storage location per project
   - Mix of local and cloud models
   - For general enterprise use

4. **Cloud** (Standard Security)
   - Full cloud capabilities
   - Best performance and features
   - For non-sensitive projects

## AI Model Strategy

### Model Provider Interface

```python
# core/models/base.py
from typing import Protocol, Optional, Dict, Any

class ModelProvider(Protocol):
    """Unified interface for all model providers"""
    
    async def complete(
        self, 
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate completion from model"""
        ...
    
    def supports_vision(self) -> bool:
        """Check if model supports image inputs"""
        return False
    
    def supports_tools(self) -> bool:
        """Check if model supports function calling"""
        return False
    
    def supports_streaming(self) -> bool:
        """Check if model supports streaming responses"""
        return False
    
    def get_context_window(self) -> int:
        """Return maximum context length"""
        ...
```

### Custom Pydantic + JSON Parsing

```python
# core/parsing/extractor.py
from typing import Type, TypeVar, Tuple
from pydantic import BaseModel, ValidationError
import json
import re

T = TypeVar('T', bound=BaseModel)

class StructuredExtractor:
    """Extract and validate structured data from LLM responses"""
    
    def __init__(self):
        self.json_patterns = [
            # Common patterns for finding JSON in text
            r'```json\s*(\{.*?\})\s*```',
            r'```\s*(\{.*?\})\s*```',
            r'(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})',
        ]
    
    async def extract(
        self, 
        text: str, 
        model_class: Type[T],
        strict: bool = False
    ) -> Tuple[bool, Optional[T], Optional[str]]:
        """
        Extract structured data from text
        Returns: (success, parsed_object, error_message)
        """
        # First try: Direct JSON parsing
        try:
            data = json.loads(text)
            return True, model_class(**data), None
        except (json.JSONDecodeError, ValidationError):
            pass
        
        # Second try: Extract JSON from text
        for pattern in self.json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    obj = model_class(**data)
                    return True, obj, None
                except (json.JSONDecodeError, ValidationError) as e:
                    continue
        
        # Third try: Fallback parsing (if not strict)
        if not strict:
            return self._fallback_parse(text, model_class)
        
        return False, None, "Could not extract valid JSON"
```

## Agent Architecture

### Coordinating Agent

```python
# core/agents/coordinator.py
class CoordinatingAgent:
    """Main orchestrator that manages specialized agents"""
    
    def __init__(self, model_provider: ModelProvider):
        self.model = model_provider
        self.agents = {
            'stpa-sec': STPASecAgent(model_provider),
            'stride': STRIDEAgent(model_provider),
            'code': CodeAnalysisAgent(model_provider),
            'cve': CVESearchAgent(model_provider),
        }
        self.context = ConversationContext()
    
    async def handle_user_request(
        self, 
        message: str,
        session_id: str
    ) -> AgentResponse:
        """Process user request and coordinate agents"""
        
        # 1. Understand intent
        intent = await self._analyze_intent(message)
        
        # 2. Delegate to appropriate agents
        if intent.requires_analysis:
            tasks = self._plan_analysis_tasks(intent)
            results = await self._execute_tasks(tasks)
            
        # 3. Synthesize results
        response = await self._synthesize_response(results)
        
        # 4. Update context
        self.context.add_interaction(message, response)
        
        return response
```

### Specialized Agent Example

```python
# core/agents/stpa_sec.py
class STPASecAgent:
    """Specialized agent for STPA-Sec analysis"""
    
    def __init__(self, model_provider: ModelProvider):
        self.model = model_provider
        self.extractor = StructuredExtractor()
        self.prompts = PromptLibrary.load('stpa-sec')
    
    async def analyze(
        self, 
        system_description: str,
        context: Optional[AnalysisContext] = None
    ) -> STPASecAnalysis:
        """Perform complete STPA-Sec analysis"""
        
        results = STPASecAnalysis()
        
        # Step 1: Identify losses
        losses = await self._identify_losses(system_description)
        results.losses = losses
        
        # Step 2: Identify hazards
        hazards = await self._identify_hazards(
            system_description, losses
        )
        results.hazards = hazards
        
        # Continue through all steps...
        
        return results
```

## User Interface Design

### Layout Concept

```
┌─────────────────────────────────────────────────────────┐
│  Security Analysis Platform  | Project: BankingSystem    │
├─────────────┬─────────────┬─────────────────────────────┤
│   System    │  Analysis   │      Conversational         │
│   Browser   │   Canvas    │        Assistant            │
│             │             │                             │
│ 📁 Files    │ 📊 STPA-Sec │ 🤖 "I've analyzed your     │
│  └─ src/    │  └─ Losses  │ system and identified       │
│    └─ api/  │  └─ Hazards │ several security concerns.  │
│  └─ docs/   │             │ Would you like me to focus  │
│             │ 📊 STRIDE   │ on the API endpoints first?"│
│ ➕ Upload   │  └─ Threats │                             │
│             │             │ [Show detailed analysis]    │
├─────────────┴─────────────┴─────────────────────────────┤
│         System Diagram / Visualization Area              │
│     [Interactive control structure diagram here]         │
└─────────────────────────────────────────────────────────┘
```

### Interaction Modes

1. **Full Auto Analysis**
   - User uploads system description/code
   - System runs all selected analyses automatically
   - Results presented for review and refinement

2. **Guided Analysis**
   - Conversational agent guides through each step
   - User provides input at decision points
   - More interactive and educational

3. **Incremental Analysis**
   - User provides partial information
   - Agent asks clarifying questions
   - Analysis builds progressively

## Implementation Roadmap

### Phase 1: MVP (Weeks 1-4)
- [ ] Core architecture setup
- [ ] Custom Pydantic parsing implementation
- [ ] Basic STPA-Sec and STRIDE agents
- [ ] Simple CLI interface
- [ ] Local storage only
- [ ] Single model support (Ollama)

### Phase 2: Web Interface (Weeks 5-8)
- [ ] FastAPI backend
- [ ] React frontend with chat interface
- [ ] File upload and management
- [ ] Basic visualization (diagrams)
- [ ] Session management

### Phase 3: Agent Enhancement (Weeks 9-12)
- [ ] Coordinating agent implementation
- [ ] Context management
- [ ] Multiple model support
- [ ] Plugin system for new analyses
- [ ] Export capabilities

### Phase 4: Collaboration (Weeks 13-16)
- [ ] Multi-user support
- [ ] Version control for analyses
- [ ] Cloud storage option
- [ ] Real-time updates (WebSockets)

### Phase 5: Advanced Features (Weeks 17-20)
- [ ] CVE integration
- [ ] Compliance mapping
- [ ] Custom report generation
- [ ] API for external integration

## Technology Stack

### Backend
- **Framework**: FastAPI (async, modern, fast)
- **Language**: Python 3.12+
- **Task Queue**: Celery (for long-running analyses)
- **Cache**: Redis
- **Database**: PostgreSQL + Neo4j (graph data)

### Frontend
- **Framework**: React with TypeScript
- **UI Library**: Ant Design or Material-UI
- **State Management**: Zustand or Redux Toolkit
- **Charts**: D3.js / Recharts
- **Diagrams**: Cytoscape.js or React Flow

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose (dev), Kubernetes (production)
- **Storage**: MinIO (S3-compatible) for local development
- **Monitoring**: Prometheus + Grafana

## Plugin System Design

### Plugin Interface

```python
# core/plugins/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AnalysisPlugin(ABC):
    """Base class for all analysis plugins"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique plugin identifier"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description"""
        pass
    
    @abstractmethod
    async def analyze(
        self, 
        system_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AnalysisResult:
        """Perform the analysis"""
        pass
    
    def get_prompts(self) -> Dict[str, str]:
        """Return plugin-specific prompts"""
        return {}
    
    def get_ui_config(self) -> Dict[str, Any]:
        """Return UI configuration for the plugin"""
        return {
            'icon': 'DefaultIcon',
            'color': '#1890ff',
            'displayName': self.name
        }
```

### Plugin Loading

```python
# core/plugins/loader.py
import importlib
import inspect
from pathlib import Path

class PluginLoader:
    """Dynamic plugin loading system"""
    
    def __init__(self, plugin_dir: Path):
        self.plugin_dir = plugin_dir
        self.plugins = {}
    
    def load_plugins(self):
        """Load all plugins from plugin directory"""
        for file in self.plugin_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
                
            module = importlib.import_module(f"plugins.{file.stem}")
            
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, AnalysisPlugin) and 
                    obj != AnalysisPlugin):
                    
                    plugin = obj()
                    self.plugins[plugin.name] = plugin
```

## Configuration Management

### Application Configuration

```yaml
# config/app.yaml
app:
  name: "Security Analysis Platform"
  version: "1.0.0"
  
server:
  host: "0.0.0.0"
  port: 8000
  cors_origins: ["http://localhost:3000"]
  
analysis:
  default_frameworks: ["stpa-sec", "stride"]
  max_file_size: "100MB"
  timeout_seconds: 300
  
models:
  default_provider: "ollama"
  default_model: "llama3"
  
  providers:
    ollama:
      base_url: "http://localhost:11434"
      models: ["llama3", "mistral", "codellama"]
      
    openai:
      models: ["gpt-4", "gpt-4-turbo-preview"]
      requires_api_key: true
      
    anthropic:
      models: ["claude-3-opus", "claude-3-sonnet"]
      requires_api_key: true
```

## Next Steps

1. **Set up repository structure** following this architecture
2. **Implement core parsing system** with Custom Pydantic
3. **Create basic agent framework** with coordinator
4. **Build simple CLI** for testing
5. **Design and implement web UI**
6. **Add specialized agents** incrementally
7. **Implement plugin system** for extensibility

## Development Principles

1. **Model Agnostic**: Support any LLM through provider interface
2. **Deployment Flexible**: Run anywhere from laptop to cloud
3. **Security First**: Assume sensitive data, encrypt by default
4. **User Centric**: Intuitive interface, helpful agent interactions
5. **Extensible**: Easy to add new analyses and integrations
6. **Testable**: Comprehensive test coverage, especially for parsing

---

*This architecture supports a self-service security analysis platform with coordinating agents, suitable for both rapid prototyping and production deployment.*