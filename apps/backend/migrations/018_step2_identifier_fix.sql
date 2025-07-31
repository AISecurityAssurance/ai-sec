-- Migration: 018_step2_identifier_fix.sql
-- Description: Ensure all Step 2 columns exist
-- Created: 2025-01-30

-- Drop and recreate system_components table with all columns
DROP TABLE IF EXISTS control_hierarchies CASCADE;
DROP TABLE IF EXISTS trust_boundaries CASCADE;
DROP TABLE IF EXISTS process_models CASCADE;
DROP TABLE IF EXISTS feedback_mechanisms CASCADE;
DROP TABLE IF EXISTS control_action_contexts CASCADE;
DROP TABLE IF EXISTS control_actions CASCADE;
DROP TABLE IF EXISTS system_components CASCADE;

-- Recreate with full schema
CREATE TABLE system_components (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    component_type VARCHAR CHECK (component_type IN ('controller', 'controlled_process', 'both')) NOT NULL,
    description TEXT,
    abstraction_level VARCHAR CHECK (abstraction_level IN ('service', 'subsystem', 'component')) DEFAULT 'service',
    source VARCHAR,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recreate control_actions with all columns
CREATE TABLE control_actions (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL,
    controller_id VARCHAR REFERENCES system_components(id),
    controlled_process_id VARCHAR REFERENCES system_components(id),
    action_name VARCHAR NOT NULL,
    action_description TEXT,
    action_type VARCHAR,
    timing_requirements JSONB,
    authority_level VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recreate other tables
CREATE TABLE control_action_contexts (
    id VARCHAR PRIMARY KEY,
    control_action_id VARCHAR REFERENCES control_actions(id) ON DELETE CASCADE,
    required_system_state VARCHAR NOT NULL,
    prohibited_states TEXT[],
    preconditions JSONB,
    postconditions JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE feedback_mechanisms (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL,
    source_process_id VARCHAR REFERENCES system_components(id),
    target_controller_id VARCHAR REFERENCES system_components(id),
    feedback_name VARCHAR NOT NULL,
    information_type VARCHAR NOT NULL,
    information_content TEXT,
    timing_characteristics JSONB,
    reliability_requirements JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE process_models (
    id VARCHAR PRIMARY KEY,
    controller_id VARCHAR REFERENCES system_components(id),
    model_name VARCHAR NOT NULL,
    state_variables JSONB,
    update_sources TEXT[],
    update_frequency VARCHAR,
    staleness_tolerance VARCHAR,
    assumptions JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE trust_boundaries (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL,
    boundary_name VARCHAR NOT NULL,
    boundary_type VARCHAR,
    component_a_id VARCHAR REFERENCES system_components(id),
    component_b_id VARCHAR REFERENCES system_components(id),
    trust_direction VARCHAR CHECK (trust_direction IN ('bidirectional', 'a_trusts_b', 'b_trusts_a', 'none')),
    authentication_method VARCHAR,
    authorization_method VARCHAR,
    data_protection_requirements JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE control_hierarchies (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    parent_component_id VARCHAR REFERENCES system_components(id),
    child_component_id VARCHAR REFERENCES system_components(id),
    relationship_type VARCHAR,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(parent_component_id, child_component_id)
);

-- Create operational_modes if it doesn't exist
CREATE TABLE IF NOT EXISTS operational_modes (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    mode_name VARCHAR NOT NULL,
    description TEXT,
    entry_conditions JSONB,
    exit_conditions JSONB,
    available_control_actions TEXT[],
    restricted_actions TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recreate indexes
CREATE INDEX idx_system_components_analysis ON system_components(analysis_id);
CREATE INDEX idx_control_actions_controller ON control_actions(controller_id);
CREATE INDEX idx_control_actions_process ON control_actions(controlled_process_id);
CREATE INDEX idx_feedback_source ON feedback_mechanisms(source_process_id);
CREATE INDEX idx_feedback_target ON feedback_mechanisms(target_controller_id);
CREATE INDEX idx_trust_boundaries_components ON trust_boundaries(component_a_id, component_b_id);
CREATE INDEX idx_components_identifier ON system_components(analysis_id, identifier);