# Security Analysis System - Project Documentation

## Executive Summary

This document outlines the design and implementation plan for an automated security analysis system that combines multiple security frameworks (STPA-Sec, STRIDE, MAESTRO, etc.) to provide comprehensive vulnerability assessment. The system aims to automate the entire security analysis process while allowing interactive collaboration between security analysts and customers.

## Vision & Long-Term Goals

### Ultimate Vision
An automated security analysis system for systems security engineering design and analysis that can:
- Take natural language prompts and design entire systems with security built-in from the start
- Provide interactive web-based collaboration between analysts and customers
- Generate comprehensive reports for compliance audits and system documentation
- Eliminate weeks of back-and-forth emails through real-time collaborative analysis

### Key Long-Term Features
1. **Multi-Framework Analysis**: Support for STPA-Sec, STRIDE, MAESTRO, PASTA, LINDDUN, DREAD, OCTAVE, HAZOP
2. **Interactive Diagramming**: Clickable components with detailed information and meaningful icons
3. **Real-Time Collaboration**: Multiple users modifying and analyzing simultaneously
4. **Version Control**: Complete history of changes and analyses
5. **Compliance Integration**: Automatic mapping to GDPR, HIPAA, PCI-DSS, etc.
6. **Advanced Inputs**: PDFs, images, GitHub repos, incident reports, web-scraped reviews
7. **Multi-LLM Support**: OpenAI, Anthropic, Google Gemini, Llama, Ollama, Grok, in-house models

## Immediate Prototype Goals (Week 1-2)

### Primary Objective
Demonstrate that STRIDE + STPA-Sec provides better security analysis than STRIDE alone, with comprehensive and thorough vulnerability coverage.

### Week 1 Deliverables
1. **CLI Tool** with:
   - Text input support
   - Image input support (for existing diagrams)
   - GitHub repository analysis
   - Full STPA-Sec analysis (all 4 steps)
   - Complete STRIDE analysis
   - STRIDE-to-STPA-Sec integration
   - Markdown report generation

2. **Analysis Quality Focus**:
   - Comprehensive vulnerability identification
   - System-level security issues (STPA-Sec strength)
   - Component-level threats (STRIDE strength)
   - Integration insights showing combined value

### Week 2 Deliverables
1. **Basic Web Interface**:
   - Document upload (text, PDF, images)
   - Analysis results viewer
   - Basic diagram generation
   - Report export (PDF, Markdown)

2. **Additional Integrations**:
   - Multi-framework synthesis
   - Quick assessment mode
   - Basic compliance mapping

## Technology Stack

### Selected Technologies
- **Frontend**: React
- **Backend**: Python with FastAPI
- **LLM Integration**: OpenAI API (initially)
- **Database**: SQLite (prototype), PostgreSQL (production)
- **Containerization**: Docker
- **Cloud**: AWS (primary), GCP-compatible design

### Architecture Decisions
- **Python/FastAPI**: Leverages existing Python expertise, excellent async support
- **SQLite**: Zero setup for prototype, easy migration path
- **Docker**: Cloud-agnostic deployment
- **LLM Abstraction**: Easy provider switching

## Project Structure

```
security-analysis-prototype/
├── cli/
│   ├── analyzer.py              # Main CLI entry point
│   ├── input_handlers.py        # Handle text, images, GitHub
│   └── report_generator.py      # Markdown/PDF generation
├── core/
│   ├── prompts/                 # Prompt library (from prototype1)
│   │   ├── stpa-sec/
│   │   │   ├── master.txt
│   │   │   ├── step-1.txt
│   │   │   ├── step-2.txt
│   │   │   ├── step-3.txt
│   │   │   └── step-4.txt
│   │   ├── stride/
│   │   │   └── master.txt
│   │   ├── integrations/
│   │   │   ├── stride-to-stpa-sec.txt
│   │   │   ├── multi-framework-synthesis.txt
│   │   │   └── [other integrations]
│   │   └── system-categorization/
│   │       └── categorizer.txt
│   ├── agents/
│   │   ├── base_agent.py        # Common agent functionality
│   │   ├── categorizer.py       # System type identification
│   │   ├── stpa_sec.py         # STPA-Sec implementation
│   │   ├── stride.py           # STRIDE implementation
│   │   └── integrator.py       # Framework integration logic
│   ├── models/
│   │   ├── analysis.py         # Data models for analysis
│   │   ├── system.py           # System representation
│   │   └── findings.py         # Security findings model
│   ├── llm/
│   │   ├── client.py           # LLM abstraction layer
│   │   ├── providers/
│   │   │   ├── openai.py
│   │   │   ├── anthropic.py
│   │   │   └── base.py
│   │   └── prompt_manager.py   # Prompt versioning/loading
│   └── utils/
│       ├── image_analyzer.py   # Extract info from diagrams
│       ├── github_fetcher.py   # Clone and analyze repos
│       └── pdf_extractor.py    # PDF text extraction
├── web/
│   ├── backend/
│   │   ├── main.py            # FastAPI application
│   │   ├── api/
│   │   │   ├── analysis.py    # Analysis endpoints
│   │   │   ├── reports.py     # Report generation
│   │   │   └── diagrams.py    # Diagram endpoints
│   │   ├── models/            # Pydantic models
│   │   └── services/          # Business logic
│   └── frontend/
│       ├── src/
│       │   ├── components/
│       │   │   ├── AnalysisViewer.jsx
│       │   │   ├── DiagramEditor.jsx
│       │   │   └── ReportExporter.jsx
│       │   ├── pages/
│       │   └── services/
│       └── package.json
├── tests/
│   ├── test_systems/          # Known vulnerable systems
│   ├── unit/
│   └── integration/
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── docs/
│   ├── API.md
│   ├── ANALYSIS_GUIDE.md
│   └── DEPLOYMENT.md
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables
└── README.md

```

## Implementation Plan

### Phase 1: CLI Foundation (Days 1-3)
1. Set up project structure and dependencies
2. Implement LLM client abstraction
3. Create prompt loading system
4. Build system categorizer agent
5. Implement STPA-Sec analysis pipeline
6. Implement STRIDE analysis
7. Create STRIDE-to-STPA-Sec integration
8. Build report generator

### Phase 2: Testing & Refinement (Days 4-5)
1. Test on OWASP Juice Shop vulnerabilities
2. Test on DVWA (Damn Vulnerable Web Application)
3. Refine prompts based on results
4. Optimize analysis pipeline
5. Document findings and improvements

### Phase 3: Web Interface (Days 6-10)
1. Set up FastAPI backend
2. Create React frontend structure
3. Implement file upload endpoints
4. Build analysis viewer components
5. Add basic diagram generation
6. Create report export functionality

### Phase 4: Integration & Polish (Days 11-14)
1. Add additional framework integrations
2. Implement basic diagram editing
3. Create comprehensive test suite
4. Write deployment documentation
5. Prepare demo materials

## Test Systems

### Primary Test Targets
1. **OWASP Juice Shop** (https://owasp.org/www-project-juice-shop/)
   - Modern web application with known vulnerabilities
   - Good for testing web-specific threats
   - Well-documented security issues

2. **DVWA** (https://github.com/digininja/DVWA)
   - Deliberately vulnerable web application
   - Multiple vulnerability levels
   - Good for benchmarking detection capabilities

### Additional Test Candidates
- **WebGoat** (OWASP): Java-based vulnerable app
- **Mutillidae II**: Web pen-test practice application
- **NodeGoat**: Node.js vulnerable application
- **Vulnerable Node**: Express.js vulnerable app

## Success Metrics

### Prototype Success Criteria
1. **Analysis Completeness**: Identifies 80%+ of known vulnerabilities
2. **Integration Value**: STRIDE+STPA-Sec finds 30%+ more issues than STRIDE alone
3. **Speed**: Complete analysis in < 10 minutes (vs hours manually)
4. **Usability**: Security team can run analysis without training
5. **Report Quality**: Generated reports require < 20% manual editing

### Key Demonstrations
1. Show system-level vulnerabilities only STPA-Sec catches
2. Demonstrate how integration provides deeper insights
3. Prove automation doesn't sacrifice analysis quality
4. Show speed improvement over manual analysis

## Development Guidelines

### Code Organization
- **Modular Design**: Each framework in separate module
- **Clear Interfaces**: Well-defined agent contracts
- **Async First**: Use async/await for LLM calls
- **Type Hints**: Full Python type annotations
- **Documentation**: Docstrings for all public functions

### LLM Integration Best Practices
```python
class BaseAgent:
    async def analyze(self, system_description: str) -> AnalysisResult:
        """Base analysis method for all agents"""
        pass

class LLMClient:
    async def complete(self, prompt: str, model: str = "gpt-4") -> str:
        """Abstract LLM completion interface"""
        pass
```

### Error Handling
- Graceful degradation if LLM calls fail
- Retry logic with exponential backoff
- Clear error messages for users
- Logging for debugging

## Environment Setup

### Required Environment Variables
```bash
# .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=sqlite:///./analysis.db
SECRET_KEY=your-secret-key
ENVIRONMENT=development
```

### Python Dependencies
```txt
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
openai==1.6.1
anthropic==0.8.1
Pillow==10.1.0  # Image processing
PyPDF2==3.0.1   # PDF extraction
python-multipart==0.0.6  # File uploads
markdown==3.5.1
weasyprint==60.1  # PDF generation
aiofiles==23.2.1
python-jose==3.3.0  # JWT tokens
GitPython==3.1.40  # GitHub repo analysis
```

## Next Steps for Claude Code

### Immediate Actions
1. Create new project directory: `security-analysis-prototype`
2. Copy prompts from `prototype1/prompts/` to `core/prompts/`
3. Set up Python virtual environment
4. Install dependencies from requirements.txt
5. Create `.env` file with API keys
6. Start with `cli/analyzer.py` implementation

### First Code Tasks
```python
# cli/analyzer.py - Starting point
import asyncio
from pathlib import Path
from core.agents.categorizer import SystemCategorizer
from core.agents.stpa_sec import StpaSecAgent
from core.agents.stride import StrideAgent

async def main():
    # 1. Load system description
    # 2. Categorize system
    # 3. Run STPA-Sec analysis
    # 4. Run STRIDE analysis
    # 5. Integrate results
    # 6. Generate report
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

### Testing Approach
1. Start with simple test case (basic web app description)
2. Verify each analysis step independently
3. Test integration logic
4. Run against OWASP Juice Shop
5. Compare results with known vulnerabilities

## Contact and Resources

### Team Communication
- Primary: [Your preferred communication method]
- Code Repository: [GitHub/GitLab URL when created]
- Documentation: This document + inline code comments

### External Resources
- STPA Handbook: [Reference for STPA-Sec implementation]
- STRIDE Documentation: [Microsoft threat modeling]
- OWASP Testing Guide: [For validation]

## Appendix: Prompt Integration Strategy

### Prompt Versioning
- Store prompts in text files for easy editing
- Version control through Git
- Load dynamically at runtime
- Allow prompt switching for testing

### Integration Flow
1. System Categorization → Determines frameworks
2. STPA-Sec Step 1-4 → Complete system analysis
3. STRIDE → Component threat modeling
4. STRIDE-to-STPA-Sec → Integration insights
5. Multi-framework Synthesis → Unified findings
6. Report Generation → Comprehensive output

---

*Document Version: 1.0*  
*Last Updated: [Current Date]*  
*Next Review: After Week 1 Prototype Completion*