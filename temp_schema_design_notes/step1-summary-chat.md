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

System description (text file or interactive)
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
