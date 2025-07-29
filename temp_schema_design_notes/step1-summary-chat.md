STPA-Sec Step 1: Problem Framing Implementation Summary
Project Overview
We are building an AI-powered system to automate STPA-Sec (System-Theoretic Process Analysis for Security) analysis, starting with Step 1: Problem Framing. This document summarizes the design decisions, schema, and implementation approach for Step 1, preparing for command-line tool development and UI design.
STPA-Sec Background
What is STPA-Sec?
STPA-Sec extends STPA (System-Theoretic Process Analysis) for security analysis. It addresses security through a strategy lens, beginning at the concept stage, rather than as a tactical bolt-on. Key principles:

Mission-First: Start with mission impact, work backwards to technical vulnerabilities
Control Theory Based: Uses control loops, feedback, and system states
Adversary as Controller: Treats adversaries as controllers solving their own control problem

STPA-Sec Process Steps

Problem Framing (our focus)
Model the Control Structure
Identify Unsafe/Unsecure Control Actions
Identify Security-Related Causal Scenarios
Wargaming

STRIDE Integration
STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) is used to:

Categorize attacks (not generate scenarios)
Bridge to security experts
Map to security solutions

Step 1: Problem Framing - Final Design
Core Principle
Step 1 maintains mission-level abstraction, focusing on:

WHAT the system does (mission)
WHAT we don't want to happen (losses)
WHAT system states enable losses (hazards)
WHO cares (stakeholders)
WHEN hazards exist (temporal nature)

Step 1 explicitly avoids:

HOW to prevent losses
HOW to implement controls
Technical mechanisms
Solution language

Database Schema
1. Problem Statements Table
sqlCREATE TABLE problem_statements (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),
    
    -- Structured components
    purpose_what TEXT NOT NULL,
    method_how TEXT NOT NULL,
    goals_why TEXT NOT NULL,
    
    -- Generated full statement
    full_statement TEXT GENERATED ALWAYS AS (
        'A System to ' || purpose_what ||
        ' by means of ' || method_how ||
        ' in order to ' || goals_why
    ) STORED,
    
    -- Context and constraints
    mission_context JSONB,
    operational_constraints JSONB,
    environmental_assumptions JSONB,
    
    -- Analysis metadata
    analysis_confidence JSONB,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
2. Losses Table
sqlCREATE TABLE losses (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),
    
    identifier VARCHAR NOT NULL, -- L1, L2, etc.
    description TEXT NOT NULL,
    loss_category VARCHAR CHECK (loss_category IN (
        'life', 'injury', 'financial', 'environmental',
        'mission', 'reputation', 'privacy', 'regulatory'
    )),
    
    severity_classification JSONB,
    mission_impact JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);
3. Loss Dependencies Table
sqlCREATE TABLE loss_dependencies (
    id VARCHAR PRIMARY KEY,
    primary_loss_id VARCHAR REFERENCES losses(id),
    dependent_loss_id VARCHAR REFERENCES losses(id),
    
    dependency_type VARCHAR CHECK (dependency_type IN (
        'enables', 'amplifies', 'triggers'
    )),
    
    dependency_strength VARCHAR CHECK (dependency_strength IN (
        'certain', 'likely', 'possible'
    )),
    
    time_relationship JSONB,
    
    UNIQUE(primary_loss_id, dependent_loss_id)
);
4. Hazards Table
sqlCREATE TABLE hazards (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),
    
    identifier VARCHAR NOT NULL,
    description TEXT NOT NULL,
    
    hazard_category VARCHAR CHECK (hazard_category IN (
        'integrity_compromised', 'availability_degraded',
        'confidentiality_breached', 'non_compliance',
        'mission_degraded', 'capability_loss'
    )),
    
    affected_system_property VARCHAR,
    environmental_factors JSONB,
    temporal_nature JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);
5. Mission Success Criteria Table
sqlCREATE TABLE mission_success_criteria (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),
    
    -- What success looks like (no prevention language)
    success_states JSONB,
    success_indicators JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);
6. Stakeholders Table
sqlCREATE TABLE stakeholders (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),
    
    name VARCHAR NOT NULL,
    stakeholder_type VARCHAR CHECK (stakeholder_type IN (
        'user', 'operator', 'owner', 'regulator',
        'partner', 'society', 'supplier'
    )),
    
    mission_perspective JSONB,
    loss_exposure JSONB,
    influence_interest JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);
7. Adversary Profiles Table
sqlCREATE TABLE adversary_profiles (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),
    
    adversary_class VARCHAR,
    profile JSONB,
    mission_targets JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);
8. Step 1 to Step 2 Bridge Table
sqlCREATE TABLE step1_step2_bridge (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),
    
    control_needs JSONB,
    implied_boundaries JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);
Agent Architecture
Orchestrator
pythonclass Step1ProblemFramingOrchestrator:
    def __init__(self):
        self.agents = {
            'mission_analyst': MissionAnalystAgent(),
            'loss_identifier': LossIdentificationAgent(),
            'hazard_state_identifier': HazardStateIdentificationAgent(),
            'stakeholder_analyst': StakeholderAnalystAgent(),
            'adversary_analyst': AdversaryAnalystAgent(),
            'context_analyst': ContextAnalystAgent(),
            'validation_agent': Step1ValidationAgent(),
            'bridge_agent': Step1Step2BridgeAgent()
        }
Key Agent Responsibilities

Mission Analyst: Extracts purpose, method, and goals
Loss Identifier: Identifies unacceptable outcomes
Hazard State Identifier: Identifies system states that enable losses
Stakeholder Analyst: Identifies who has interest in the system
Adversary Analyst: Profiles potential adversaries (high-level)
Validation Agent: Ensures abstraction level and completeness
Bridge Agent: Prepares transition to Step 2

Critical Validation Rules

No Solution Language: Terms like "prevent", "mitigate", "control" should not appear
Hazards as States: Not actions or failures
Loss Coverage: Every loss needs associated hazards
Stakeholder Alignment: All stakeholder success perspectives captured

Example Banking System Analysis
json{
    "problem_statement": {
        "purpose_what": "enable secure management of customer financial assets",
        "method_how": "controlled access to banking services and transaction integrity assurance",
        "goals_why": "preserve customer trust, ensure regulatory compliance, and maintain financial stability"
    },
    "losses": [
        {
            "identifier": "L1",
            "description": "Customer financial loss",
            "category": "financial"
        }
    ],
    "hazards": [
        {
            "identifier": "H1",
            "description": "System operates with compromised transaction authorization integrity",
            "maps_to_losses": ["L1", "L3"]
        }
    ]
}
Next Steps: Command Line Tool & UI Design
Command Line Tool Requirements
The CLI tool should:

Accept Input:

System description (text, code, images, existing analysis from our tool or other tools)
Domain context
Existing analysis ID (for iterations)


Execute Analysis:

Run the same agent orchestration as web app
Store results in same database schema
Support incremental/iterative refinement


Provide Output:

JSON export of analysis
Human-readable reports
Validation results
Progress indicators


Python Library Interface:
pythonfrom stpa_sec import Step1Analyzer

analyzer = Step1Analyzer()
result = analyzer.analyze_system(
    description="Banking system that...",
    domain="financial_services"
)


UI Requirements Research Needed
Security analysts need:

Multiple Views:

Problem framing overview
Loss dependency graph
Hazard-loss mapping matrix
Stakeholder impact analysis
Temporal hazard timeline


Interactive Features:

Edit/refine analysis elements
Validate changes in real-time
Compare versions
Export for reporting


Visualization Priorities:

Loss cascade chains
Stakeholder-loss sensitivity matrix
Hazard coverage gaps
Analysis completeness metrics



Key Questions for Next Chat

CLI Architecture: Should we use Click, Typer, or another framework?
API Design: REST vs GraphQL for programmatic access?
Visualization Libraries: D3.js, Cytoscape, or other for graphs?
Report Formats: What export formats do analysts need?
Collaboration Features: How do teams work together on analysis?

Critical Implementation Notes

Maintain Abstraction: The CLI must enforce the same abstraction rules as the web app
Validation First: Run validation before persisting any changes
Versioning: Support for iterative refinement with full history
Extensibility: Design for future STPA-Sec steps (2-5)

Resources to Provide in Next Chat

STPA-Sec-Tutorial.pdf (for reference)
Current web UI implementation details
User research on analyst workflows
Example analyses for testing

This document provides the foundation for implementing a command-line interface and designing effective visualizations for STPA-Sec Step 1 analysis while maintaining the methodology's integrity and abstraction requirements.



# Iteration

  Claude Web App has provided an excellent architectural vision! Here's my analysis and what we need to clarify:

  What We Already Have:

  1. Step 1 Agents implemented with:
    - MissionAnalystAgent
    - LossIdentificationAgent
    - HazardIdentificationAgent
    - StakeholderAnalystAgent
    - ValidationAgent
    - Step1Coordinator (orchestrates all agents)
  2. Database schema for Step 1 (all tables mentioned are already created)
  3. Backend infrastructure with FastAPI (though not yet connected to Step 1 agents)

  Key Design Decisions to Discuss:

  1. State Management Architecture
    - We need a session/analysis state manager that tracks:
        - Frozen elements
      - User edits
      - Version history
      - Analysis metadata
  2. Agent Execution Modes
  # Should we have different execution modes?
  class ExecutionMode(Enum):
      FULL = "full"          # Complete analysis
      INCREMENTAL = "incremental"  # Only update changed parts
      TARGETED = "targeted"   # User specifies which agents to run
      VALIDATION_ONLY = "validation"  # Just run validation
  3. Edit Preservation Strategy
    - How do we merge AI-generated content with user edits?
    - Should we use a three-way merge (original, AI changes, user changes)?
    - Do we need conflict resolution?
  4. External AI Agent Interface
    - Should we create a simplified "security analysis as a service" API?
    - How do we handle the abstraction gap between code/architecture and mission-level analysis?

  Questions for Claude Web App:

  1. Progress Tracking: Our Step 1 agents currently complete in ~0.1 seconds. Do we need streaming for such fast operations, or is this
  for future multi-step analyses?
  2. Diagram Processing: How should we extract mission-relevant information from architecture diagrams? Should this be a separate
  pre-processing step?
  3. Code Analysis Bridge: The STPA-Sec methodology works at mission level, not code level. Should we have an intermediate "technical
  context extractor" that translates code/configs into mission-relevant statements?
  4. Versioning Granularity: Should every edit create a new version, or should we have "working drafts" with explicit commit points?

  Proposed Integration Architecture:

  # Building on what we have
  class STAPSecAnalysisEngine:
      def __init__(self):
          self.step1_coordinator = Step1Coordinator()
          self.state_manager = AnalysisStateManager()
          self.version_controller = VersionController()

      async def create_analysis(self, 
                              system_description: str,
                              domain: Optional[str] = None,
                              metadata: Optional[Dict] = None) -> str:
          """Create new analysis, return analysis_id"""

      async def run_step(self,
                        analysis_id: str,
                        step: int,
                        execution_mode: ExecutionMode = ExecutionMode.FULL,
                        frozen_elements: Optional[Dict] = None,
                        user_edits: Optional[Dict] = None) -> Dict:
          """Run specific step with state preservation"""

  Next Steps:

  1. Should we start by creating the state management layer?
  2. Or should we first build the CLI interface to test the workflow?
  3. Do we need to modify our existing agents to support incremental execution?

  What aspects should we prioritize based on your immediate needs?



# Chat with Claude Code:
The system is now ready for testing Step 1 analysis:

  1. Quick test: ./ai-sec demo - Should load pre-packaged analysis
  2. Full analysis: ./ai-sec analyze --config configs/test-gpt4-standard.yaml
  3. Development: ./ai-sec shell for interactive work

  The Docker Compose profiles provide exactly the flexibility you wanted:
  - Easy demos without complex setup
  - CLI-only mode for analysis
  - Full development environment when needed


Should we also consider hazards like regulatory reporting errors or audit trail manipulation?


# Save notes--temp
 Option A: Direct Mappings
  - Find hazards that map to catastrophic losses
  - Find losses with multiple dependencies
  - Find hazards addressed by mandatory constraints

  Option B: Intersection Analysis
  - Hazard + Loss + Adversary intersections (e.g., H-1 + L-1 + organized_crime)
  - Dependency chains (e.g., L-3 → L-2 → L-4)
  - Multiple hazards mapping to same loss (e.g., H-6, H-7, H-8 → L-5)

  Option C: Critical Pattern Detection
  - Catastrophic losses with direct hazard mappings
  - Losses that trigger other losses (cascade effects)
  - Hazards with no preventive constraints (only detective/corrective)

  For now, we're showing the three hardcoded findings. Should we:
  1. Keep these as examples of what an LLM might find?
  2. Replace with programmatically derived findings?
  3. Remove the section entirely to stay purely factual?