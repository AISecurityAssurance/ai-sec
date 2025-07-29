# Relevant Files for Claude Web App

## Overview
This document lists the key files that Claude web app should review to understand our current STPA-Sec Step 1 implementation, database design, and architecture.

## Database Schema Files

### Core Step 1 Schema
- **`apps/backend/migrations/007_stpa_sec_step1_clean.sql`** - The final, clean Step 1 database schema with all tables, constraints, and views
  - Contains: problem_statements, losses, hazards, stakeholders, adversary_profiles, etc.
  - Includes validation views and executive summary views

### Agent Support Tables
- **`apps/backend/migrations/008_step1_agent_tables_fixed.sql`** - Tables for agent execution tracking
  - Contains: agent_activity_log, agent_results

## Step 1 Agent Implementation

### Core Agent Classes
- **`apps/backend/core/agents/step1_agents/base_step1.py`** - Base class for all Step 1 agents
- **`apps/backend/core/agents/step1_agents/step1_coordinator.py`** - Orchestrates all Step 1 agents
- **`apps/backend/core/agents/step1_agents/mission_analyst.py`** - Extracts PURPOSE, METHOD, GOALS
- **`apps/backend/core/agents/step1_agents/loss_identification.py`** - Identifies unacceptable outcomes
- **`apps/backend/core/agents/step1_agents/hazard_identification.py`** - Identifies hazardous states
- **`apps/backend/core/agents/step1_agents/stakeholder_analyst.py`** - Analyzes stakeholders & adversaries
- **`apps/backend/core/agents/step1_agents/validation_agent.py`** - Validates quality & completeness

### Test Implementation
- **`apps/backend/test_step1_agents.py`** - Shows how to use the Step 1 coordinator

## Existing Backend Structure

### FastAPI Application
- **`apps/backend/main.py`** - Main FastAPI application entry point
- **`apps/backend/api/stpa_sec.py`** - Existing STPA-Sec API endpoints (currently using mock data)
- **`apps/backend/database.py`** - Database connection setup

### Models
- **`apps/backend/models/stpa_sec.py`** - Pydantic models for STPA-Sec (may need updates for Step 1)

## Design Documentation

### Schema Design Process
- **`temp_schema_design_notes/step1-summary-chat.md`** - Summary of our Step 1 schema design decisions
- **`temp_schema_design_notes/step1.md`** - Initial Step 1 abstraction level requirements

### Architecture Documents
- **`datastructures.md`** - Overall data structure design philosophy
- **`backend_ideas.md`** - Backend architecture ideas and patterns

## Key Implementation Details

### What We Have Working:
1. **Database Schema**: Complete PostgreSQL schema for Step 1 with proper constraints
2. **Step 1 Agents**: Six specialized agents that perform the actual STPA-Sec Step 1 analysis
3. **Orchestration**: Step1Coordinator that runs agents in the correct order with parallel execution
4. **Quality Validation**: Built-in quality scoring and validation
5. **Database Integration**: Agents save results directly to PostgreSQL

### What Needs Integration:
1. **API Endpoints**: Connect the Step 1 agents to FastAPI endpoints
2. **State Management**: Track analysis sessions, frozen elements, and user edits
3. **Version Control**: Implement analysis versioning
4. **CLI Interface**: Build the command-line tool
5. **External AI Agent API**: Create simplified interface for external systems

### Current Flow:
```python
# Current implementation
coordinator = Step1Coordinator()
results = await coordinator.perform_analysis(
    system_description="...",
    analysis_name="Test Analysis"
)
# Results are saved to database with analysis_id
```

### Database Connection:
- Uses asyncpg for async PostgreSQL operations
- Connection string: `postgresql://sa_user:sa_password@postgres:5432/security_analyst`
- Docker service name: `postgres`

## Important Notes:
1. The schema maintains mission-level abstraction (WHAT not HOW)
2. Agents validate abstraction level throughout analysis
3. All results are structured for Step 1 → Step 2 transition
4. Quality metrics are built into the validation process