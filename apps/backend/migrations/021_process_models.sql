-- Migration: 021_process_models.sql
-- Description: Add process models, control algorithms, and inadequate control scenarios tables
-- Created: 2025-08-01

-- Process Models table
CREATE TABLE IF NOT EXISTS process_models (
    id UUID PRIMARY KEY,
    analysis_id UUID NOT NULL REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL,
    controller_id VARCHAR,
    process_id VARCHAR,
    state_variables JSONB,
    assumptions JSONB,
    update_frequency VARCHAR,
    staleness_risk VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(identifier, analysis_id)
);

-- Control Algorithms table
CREATE TABLE IF NOT EXISTS control_algorithms (
    id UUID PRIMARY KEY,
    analysis_id UUID NOT NULL REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL,
    controller_id VARCHAR,
    name VARCHAR,
    description TEXT,
    constraints JSONB,
    decision_logic TEXT,
    conflict_resolution TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(identifier, analysis_id)
);

-- Inadequate Control Scenarios table
CREATE TABLE IF NOT EXISTS inadequate_control_scenarios (
    id UUID PRIMARY KEY,
    analysis_id UUID NOT NULL REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL,
    name VARCHAR,
    scenario_type VARCHAR,
    description TEXT,
    involved_components JSONB,
    preconditions JSONB,
    consequences JSONB,
    likelihood VARCHAR,
    severity VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(identifier, analysis_id)
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_process_models_analysis ON process_models(analysis_id);
CREATE INDEX IF NOT EXISTS idx_control_algorithms_analysis ON control_algorithms(analysis_id);
CREATE INDEX IF NOT EXISTS idx_inadequate_control_scenarios_analysis ON inadequate_control_scenarios(analysis_id);