-- Migration: 016_step2_control_structure.sql
-- Description: STPA-Sec Step 2 Control Structure Schema (State-Aware, Not State-Machine Heavy)
-- Created: 2025-01-30

-- =====================================================
-- STEP 2 CORE TABLES
-- =====================================================

-- Step 2 Analysis Metadata
CREATE TABLE step2_analyses (
    id VARCHAR PRIMARY KEY,
    step1_analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    description TEXT,
    execution_mode VARCHAR DEFAULT 'standard',
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- System Components (Controllers and Controlled Processes)
CREATE TABLE system_components (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL, -- CTRL-1, PROC-1, etc.
    name VARCHAR NOT NULL,
    component_type VARCHAR CHECK (component_type IN ('controller', 'controlled_process', 'both')) NOT NULL,
    description TEXT,
    abstraction_level VARCHAR CHECK (abstraction_level IN ('service', 'subsystem', 'component')) DEFAULT 'service',
    source VARCHAR, -- 'stakeholder_analysis', 'system_description', 'manual'
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Control Actions (Commands from Controllers to Controlled Processes)
CREATE TABLE control_actions (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL, -- CA-1, CA-2, etc.
    controller_id VARCHAR REFERENCES system_components(id),
    controlled_process_id VARCHAR REFERENCES system_components(id),
    action_name VARCHAR NOT NULL,
    action_description TEXT,
    action_type VARCHAR, -- 'command', 'configuration', 'permission', etc.
    timing_requirements JSONB, -- {'periodic': '5min', 'timeout': '30s'}
    authority_level VARCHAR, -- 'mandatory', 'optional', 'emergency'
    created_at TIMESTAMP DEFAULT NOW()
);

-- Control Action Contexts (When actions are valid/invalid)
CREATE TABLE control_action_contexts (
    id VARCHAR PRIMARY KEY,
    control_action_id VARCHAR REFERENCES control_actions(id) ON DELETE CASCADE,
    required_system_state VARCHAR NOT NULL, -- 'authenticated', 'maintenance_mode', etc.
    prohibited_states TEXT[], -- States where action is NOT allowed
    preconditions JSONB, -- Simple conditions, not formal logic
    postconditions JSONB, -- Expected state after action
    created_at TIMESTAMP DEFAULT NOW()
);

-- Feedback Mechanisms (Information from Controlled Processes to Controllers)
CREATE TABLE feedback_mechanisms (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL, -- FB-1, FB-2, etc.
    source_process_id VARCHAR REFERENCES system_components(id),
    target_controller_id VARCHAR REFERENCES system_components(id),
    feedback_name VARCHAR NOT NULL,
    information_type VARCHAR NOT NULL, -- 'status', 'measurement', 'alert', 'confirmation'
    information_content TEXT,
    timing_characteristics JSONB, -- {'frequency': 'continuous', 'latency': '<100ms'}
    reliability_requirements JSONB, -- {'availability': '99.9%', 'accuracy': 'high'}
    created_at TIMESTAMP DEFAULT NOW()
);

-- Operational Modes (System-wide states that affect control)
CREATE TABLE operational_modes (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    mode_name VARCHAR NOT NULL, -- 'normal', 'emergency', 'maintenance', 'degraded'
    description TEXT,
    entry_conditions JSONB, -- What triggers this mode
    exit_conditions JSONB, -- How to leave this mode
    available_control_actions TEXT[], -- Which CAs are valid in this mode
    restricted_actions TEXT[], -- Which CAs are prohibited
    created_at TIMESTAMP DEFAULT NOW()
);

-- Trust Boundaries (Security perimeters between components)
CREATE TABLE trust_boundaries (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL, -- TB-1, TB-2, etc.
    boundary_name VARCHAR NOT NULL,
    boundary_type VARCHAR, -- 'network', 'authentication', 'authorization', 'data_classification'
    component_a_id VARCHAR REFERENCES system_components(id),
    component_b_id VARCHAR REFERENCES system_components(id),
    trust_direction VARCHAR CHECK (trust_direction IN ('bidirectional', 'a_trusts_b', 'b_trusts_a', 'none')),
    authentication_method VARCHAR,
    authorization_method VARCHAR,
    data_protection_requirements JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Process Models (What controllers believe about system state)
CREATE TABLE process_models (
    id VARCHAR PRIMARY KEY,
    controller_id VARCHAR REFERENCES system_components(id),
    model_name VARCHAR NOT NULL,
    state_variables JSONB, -- Variables the controller tracks
    update_sources TEXT[], -- Which feedback mechanisms update this model
    update_frequency VARCHAR, -- 'real-time', 'periodic', 'event-driven'
    staleness_tolerance VARCHAR, -- How old can the data be?
    assumptions JSONB, -- What the controller assumes
    created_at TIMESTAMP DEFAULT NOW()
);

-- Control Structure Relationships (Hierarchical relationships)
CREATE TABLE control_hierarchies (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    parent_component_id VARCHAR REFERENCES system_components(id),
    child_component_id VARCHAR REFERENCES system_components(id),
    relationship_type VARCHAR, -- 'supervises', 'coordinates', 'delegates'
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(parent_component_id, child_component_id)
);

-- Step 2 Agent Results (Similar to Step 1)
CREATE TABLE step2_agent_results (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    agent_type VARCHAR NOT NULL,
    results JSONB NOT NULL,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

CREATE INDEX idx_system_components_analysis ON system_components(analysis_id);
CREATE INDEX idx_control_actions_controller ON control_actions(controller_id);
CREATE INDEX idx_control_actions_process ON control_actions(controlled_process_id);
CREATE INDEX idx_feedback_source ON feedback_mechanisms(source_process_id);
CREATE INDEX idx_feedback_target ON feedback_mechanisms(target_controller_id);
CREATE INDEX idx_trust_boundaries_components ON trust_boundaries(component_a_id, component_b_id);

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE step2_analyses IS 'Step 2 STPA-Sec analysis focusing on control structure';
COMMENT ON TABLE system_components IS 'Controllers and controlled processes in the system';
COMMENT ON TABLE control_actions IS 'Commands that flow from controllers to controlled processes';
COMMENT ON TABLE control_action_contexts IS 'State-dependent validity of control actions';
COMMENT ON TABLE feedback_mechanisms IS 'Information that flows back to controllers';
COMMENT ON TABLE operational_modes IS 'System-wide operational states';
COMMENT ON TABLE trust_boundaries IS 'Security perimeters between components';
COMMENT ON TABLE process_models IS 'What controllers believe about system state';