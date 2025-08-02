-- Migration: 021_process_models.sql
-- Description: Update process models table and add control algorithms, inadequate control scenarios tables
-- Created: 2025-08-01

-- Update existing process_models table to add missing columns
-- Note: process_models table already exists from migration 016, we need to add missing columns
ALTER TABLE process_models ADD COLUMN IF NOT EXISTS analysis_id VARCHAR;
ALTER TABLE process_models ADD COLUMN IF NOT EXISTS identifier VARCHAR;
ALTER TABLE process_models ADD COLUMN IF NOT EXISTS process_id VARCHAR;
ALTER TABLE process_models ADD COLUMN IF NOT EXISTS staleness_risk VARCHAR;

-- Add foreign key constraint for analysis_id if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'process_models_analysis_id_fkey'
    ) THEN
        ALTER TABLE process_models 
        ADD CONSTRAINT process_models_analysis_id_fkey 
        FOREIGN KEY (analysis_id) REFERENCES step2_analyses(id) ON DELETE CASCADE;
    END IF;
END $$;

-- Add unique constraint if not exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'process_models_identifier_analysis_id_key'
    ) THEN
        ALTER TABLE process_models ADD CONSTRAINT process_models_identifier_analysis_id_key UNIQUE(identifier, analysis_id);
    END IF;
END $$;

-- Control Algorithms table
CREATE TABLE IF NOT EXISTS control_algorithms (
    id UUID PRIMARY KEY,
    analysis_id VARCHAR NOT NULL REFERENCES step2_analyses(id) ON DELETE CASCADE,
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
    analysis_id VARCHAR NOT NULL REFERENCES step2_analyses(id) ON DELETE CASCADE,
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