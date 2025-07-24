# Backend Ideas 

# Colleague's ask
A couple of things we can think about adding:
For the testing arena I like the idea of testing multiple variants but I also think it could be call if you could switch the backing LLM you were testing with. Maybe we keep that as a separate option so it doesn't get confusing

In the same vein as the variants it would be cool if we had a versioning system so that the analysis could be realtime, within a couple of seconds after submitting. That way you could also version the inputs and the threat models. For that as well we would need like a beginning flow which is where you upload your architecture diagram, textual description, etc

# We want an AI agent system
The Security Analyst (SA) agent is a chat and orchestrator.  It can both respond to the user's requests as well as run all AI agents. 
- Should the SA agent have a separate agent for chat?

## What the SA Agent can do
- Launch analysis given inputs.
- Make changes to current analysis based on user requests (i.e., user asks to update a specific section or table, add to the table, etc. generate/modify/delete plots, use a specific tool for a plot/diagram.) Essentially, the SA agent must call the right tools to update the Analysis Canvas to assist the user in the analysis.


## Short-term vision--rapid prototype
- A tool that can perform a basic analysis on all selected analysis plugins.
- A tool that can answer user's questions about the analysis.
- A tool that can re-run an analysis given user's changes or requests

## Medium term vision
- SA Agent can add new context to the Analysis Canvas using user specified tools
- SA Agent can interact with external tools (via MCP) to add new contact or further analysis goal of the user
- Modify exiting analyses reports based on feedback from user.

## Long term vision 
- SA Agent can run a fully customizable security analysis, create a comprehensive report based on all anaysis plugins, suggest additional plugins, verify requirements are met given compliance-based plugins, suggest new compliance analysis or threat/security analysis plugins/additions, completely control the Analysis Canvas making changes based on the user's requests
- Run a fully automated security analysis that can be sent to another AI agent (or human) who is designing and building tools (i.e., an iterative process between AI agents that build the software and the SA Agent that analysis security and suggests improvement to re-enforce security and align with various regulations and compliance standards).
- A tool that can gather information from tickets and user feedback and integrate into the security analysis.  Provide summaries of tickets and user feedback (etc.)


# Backend
- We need a versioning system
- We need to save all artifacts, maintain artifact state, re-load saved analyses, generate summary reports (based on user request) for one or multiple analyses (human readable).

## Saving analyses
We need to figure out how to store all the analysis components so that can be used to repopulate the Analysis Canvas.  Here are some considerations.
### Diagrams
- diagrams should be drawn based on a graph database.  We expect using the same components and relationships for different types of diagrams (i.e., process flow diagrams, user friendly diagrams with appropriate icons, diagrams that contain more component information).  Entities will include additional information (for example, click on a component in a diagram, add/edt/delete information, show different types of information in the diagram).  Relationships may change.  To be useful, the user needs to be able to change relationships, updating both the diagram and the database.
- Diagrams need to be importable into other diagramming software based on user needs.
- The diagram components should come from the other analyses entities.  

### Tracing STPA-Sec
- mitigations need to be traced to stakeholder requirements for security.  The user should be able to click on a mitigation and select Show Trace to Stakeholder requirements and possibly a map of all other components (like a mind map or something.)


How do we develop a backend that does all of this?



# WORK IN PROGRESS
Update Todos
  ⎿  ☐ Set up Python environment with uv package manager and pyproject.toml   
     ☐ Implement configuration system (settings.py) with environment variables
     ☐ Set up database models and Pydantic schemas
     ☐ Implement database setup and Alembic migrations
     ☐ Create Docker configuration for PostgreSQL, Redis, and Neo4j
     ☐ Implement base agent functionality and template mapper
     ☐ Implement STPA-Sec agent (priority - others depend on it)
     ☐ Implement WebSocket manager for real-time updates
     ☐ Implement API routes (analysis, artifacts, chat)
     ☐ Implement remaining framework agents (STRIDE, PASTA, etc.)
     ☐ Add context management with LlamaIndex
     ☐ Create tests for agents and API endpoints

⏺ Backend Implementation Plan

  Phase 1: Foundation Setup (Days 1-2)

  1. Environment Setup
    - Configure pyproject.toml with project metadata and dependencies
    - Set up uv package manager for fast dependency management
    - Create Makefile with common development tasks
    - Configure .env.example with required environment variables
  2. Configuration System
    - Implement config/settings.py using Pydantic Settings
    - Support for multiple environments (dev, staging, prod)
    - Validation for API keys and service URLs
    - Connection strings for PostgreSQL, Redis, and Neo4j
  3. Database Foundation
    - Set up SQLAlchemy models in core/models/analysis.py
    - Create Pydantic schemas in core/models/schemas.py
    - Implement database connection in storage/database.py
    - Configure Alembic for migrations

  Phase 2: Core Infrastructure (Days 3-4)

  1. Docker Services
    - Create docker-compose.yml for local development
    - PostgreSQL for analysis data
    - Redis for caching and session management
    - Neo4j for graph-based analysis relationships
  2. Base Agent System
    - Enhance core/agents/base.py with:
        - Structured output generation
      - Template mapping capabilities
      - Error handling and retry logic
      - Progress tracking
  3. Template Mapping System
    - Implement core/templates/mapper.py
    - Map agent outputs to frontend template structures
    - Validate outputs against expected schemas

  Phase 3: Agent Implementation (Days 5-7)

  1. STPA-Sec Agent (Priority - others depend on it)
    - Implement core/agents/framework_agents/stpa_sec.py
    - Parse system descriptions into structured components
    - Generate control structures and hazard analysis
    - Output in frontend-compatible format
  2. WebSocket Manager
    - Implement api/websocket.py for real-time updates
    - Handle connection lifecycle
    - Broadcast analysis progress
    - Error handling and reconnection logic
  3. API Routes
    - Implement api/routes/analysis.py:
        - POST /analysis/start - Start new analysis
      - GET /analysis/{id}/status - Get analysis status
      - POST /analysis/{id}/section/rerun - Re-run specific section
    - Implement api/routes/chat.py:
        - POST /chat/query - Query analysis results
      - WebSocket /ws/analysis/{id} - Real-time updates

  Phase 4: Advanced Features (Days 8-10)

  1. Additional Framework Agents
    - STRIDE - Threat modeling
    - PASTA - Process for Attack Simulation
    - DREAD - Risk assessment
    - Others as time permits
  2. Context Management
    - Implement core/memory/context_manager.py
    - Use LlamaIndex for efficient retrieval
    - Share STPA-Sec results with other agents
    - Manage context window efficiently
  3. Integration Features
    - Cross-framework analysis integration
    - Artifact storage and retrieval
    - Version control for analyses

  Key Design Decisions:

  1. Async First: All I/O operations will be async for performance
  2. Template Alignment: Every agent output must map to frontend templates
  3. Progressive Enhancement: Start with STPA-Sec, add frameworks incrementally
  4. Real-time Updates: WebSocket for live analysis progress
  5. Error Resilience: Continue analysis even if one agent fails

  Questions Before Starting:

  1. LLM Provider: Which LLM API should be the primary (OpenAI, Anthropic, or both)?
  2. Authentication: Do we need user authentication for the MVP, or can we defer this?
  3. Deployment: Are we targeting local deployment first, or cloud-ready from the start?
  4. Data Persistence: Should we implement full analysis versioning from the start, or just store the latest?
  5. Performance: Any specific performance requirements (e.g., max analysis time)?


  Things to keep in mind:
  - Remember the issue we had with preserving state when opening in a new tab/window.  Keep this in mind as something that is important.  


  5. Running the Tests

  # One-time setup
  ./integration-tests/setup-tests.sh

  # Run all tests
  ./integration-tests/run-integration-tests.sh

  # Or run manually
  docker-compose -f docker-compose.test.yml up -d
  cd integration-tests
  npm test


   1. Pull the latest changes:
  git pull origin main
  2. Create .env file with your API keys:
  OPENAI_API_KEY=your-key
  ANTHROPIC_API_KEY=your-key
  3. Run the setup:
  ./integration-tests/setup-tests.sh
  4. Run the tests:
  ./integration-tests/run-integration-tests.sh



  # Future iterations
  https://www.datagravity.dev/p/agent-infrastructure-and-control?utm_source=tldrdata



   Hm.  I'm thinking something more intuitive.  Users are accustomed to seeing a dropdown filepicker menu when saving to local storage.  For saving to 
  Cloud, the should provide a bucket address.  To export (no clue what they'd export it to), let's leave this our for now because we don't know any other 
  formats they could export it to.  On that note, we'll need a file extension for our app.  Since our app saves multiple components (i.e., tables, txt, 
  images, databases, whatelse?), we need to save everything in a way that it can be re-loaded in the app framework.  We should also consider saving the SA
   Agent context and/or indexing so a user can restore a previous state they were working on.  Security analysis is a long task.  Until it's automated, 
  it's likely that a human would complete the analysis in multiple sessions (shutting off their computer when they leave work) and may want to revisite 
  and rework this after some time has passed and designs have changd.  Do NOT start coding yet.  First, is this a good time to start on the save feature 
  of the app?  Second, let's discuss options and their implications for the user, app complexiting, and future growth of the app.

⏺ You're absolutely right to pause and think this through carefully. Let me analyze whether this is the right time and what our options are.

  Is this a good time to implement save functionality?

  Maybe not yet. Here's why:

  1. Incomplete Analysis Flow: We don't have actual analysis results being generated yet - we're using mock data
  2. Unknown Data Structure: We haven't fully defined what data needs to be saved (analysis results, agent context, conversation history, etc.)
  3. No Backend: Without a backend, we're limited to browser storage or file downloads
  4. Early Architecture: The app structure might change significantly as we build out real functionality

  Options for Save/Load Implementation

  Option 1: Simple JSON Export/Import (Quick Win)

  - Format: .secanalysis or .seca file (JSON-based)
  - Contents: Current state snapshot
  - Pros:
    - Quick to implement
    - Works offline
    - User has full control of their data
  - Cons:
    - No collaboration features
    - Manual file management
    - Risk of losing files

  Option 2: Browser-Based Storage First

  - Use: IndexedDB for large data, localStorage for settings
  - Pros:
    - No backend needed
    - Automatic saving
    - Works offline
  - Cons:
    - Data tied to browser/device
    - Storage limits
    - No cross-device sync

  Option 3: Full Backend Implementation

  - Architecture: REST API + PostgreSQL/MongoDB
  - Features: User accounts, cloud sync, collaboration
  - Pros:
    - Professional solution
    - Scalable
    - Enables team features
  - Cons:
    - Significant development effort
    - Requires authentication system
    - Hosting costs

  What Needs to Be Saved?

  1. Analysis Configuration
    - Selected frameworks
    - Input files/sources
    - Analysis parameters
  2. Analysis Results
    - Framework outputs
    - Generated diagrams
    - Risk assessments
    - Recommendations
  3. Working State
    - Agent conversation history
    - User annotations
    - Custom modifications
    - View preferences
  4. Metadata
    - Creation/modification dates
    - Version information
    - User notes

  Recommended Approach

  Phase 1 (Now): Focus on core functionality
  - Complete the analysis pipeline with real data
  - Define the data models clearly
  - Implement in-memory state management

  Phase 2 (Soon): Simple persistence
  - Add .seca file format (ZIP with JSON + assets)
  - Implement export/import functionality
  - Use IndexedDB for auto-save during sessions

  Phase 3 (Later): Full solution
  - Add backend with user accounts
  - Implement proper file picker (using File System Access API)
  - Add collaboration features

  File Format Proposal

  .seca (ZIP archive)
  ├── manifest.json      # Version, metadata, file index
  ├── analysis.json      # Analysis configuration and results
  ├── state.json         # UI state, preferences
  ├── conversations/     # Agent conversation history
  ├── inputs/           # Original input files
  ├── outputs/          # Generated diagrams, reports
  └── attachments/      # User-added files

  Would you like to:
  1. Continue with the current mock implementation to flesh out the UI?
  2. Start defining the data models and file format?
  3. Build out the actual analysis functionality first?