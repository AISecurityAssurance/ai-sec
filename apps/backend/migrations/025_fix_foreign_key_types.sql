-- Migration: 025_fix_foreign_key_types.sql
-- Description: Fix foreign key type mismatches across all Step 1 and Step 2 tables
-- Created: 2025-08-01

-- Fix input_analysis table - change analysis_id from UUID to VARCHAR
-- This table can reference either step1_analyses or step2_analyses, both have VARCHAR ids
ALTER TABLE input_analysis ALTER COLUMN analysis_id TYPE VARCHAR;

-- Add missing foreign key constraint for system_descriptions table
-- Migration 022 references step1_analyses but doesn't declare the foreign key properly
ALTER TABLE system_descriptions 
DROP CONSTRAINT IF EXISTS system_descriptions_analysis_id_fkey;

ALTER TABLE system_descriptions 
ADD CONSTRAINT system_descriptions_analysis_id_fkey 
FOREIGN KEY (analysis_id) REFERENCES step1_analyses(id) ON DELETE CASCADE;

-- Fix process_models table to ensure analysis_id references step2_analyses correctly
-- (This was already fixed in migration 021, but ensuring consistency)
ALTER TABLE process_models 
DROP CONSTRAINT IF EXISTS process_models_analysis_id_fkey;

ALTER TABLE process_models 
ADD CONSTRAINT process_models_analysis_id_fkey 
FOREIGN KEY (analysis_id) REFERENCES step2_analyses(id) ON DELETE CASCADE;

-- Ensure all Step 2 tables have proper foreign key constraints
ALTER TABLE control_algorithms 
DROP CONSTRAINT IF EXISTS control_algorithms_analysis_id_fkey;

ALTER TABLE control_algorithms 
ADD CONSTRAINT control_algorithms_analysis_id_fkey 
FOREIGN KEY (analysis_id) REFERENCES step2_analyses(id) ON DELETE CASCADE;

ALTER TABLE inadequate_control_scenarios 
DROP CONSTRAINT IF EXISTS inadequate_control_scenarios_analysis_id_fkey;

ALTER TABLE inadequate_control_scenarios 
ADD CONSTRAINT inadequate_control_scenarios_analysis_id_fkey 
FOREIGN KEY (analysis_id) REFERENCES step2_analyses(id) ON DELETE CASCADE;

-- Ensure control_contexts table has proper constraints
ALTER TABLE control_contexts 
DROP CONSTRAINT IF EXISTS control_contexts_analysis_id_fkey;

ALTER TABLE control_contexts 
ADD CONSTRAINT control_contexts_analysis_id_fkey 
FOREIGN KEY (analysis_id) REFERENCES step2_analyses(id) ON DELETE CASCADE;

-- Ensure operational_modes table has proper constraints  
ALTER TABLE operational_modes 
DROP CONSTRAINT IF EXISTS operational_modes_analysis_id_fkey;

ALTER TABLE operational_modes 
ADD CONSTRAINT operational_modes_analysis_id_fkey 
FOREIGN KEY (analysis_id) REFERENCES step2_analyses(id) ON DELETE CASCADE;

-- Ensure mode_transitions table has proper constraints
ALTER TABLE mode_transitions 
DROP CONSTRAINT IF EXISTS mode_transitions_analysis_id_fkey;

ALTER TABLE mode_transitions 
ADD CONSTRAINT mode_transitions_analysis_id_fkey 
FOREIGN KEY (analysis_id) REFERENCES step2_analyses(id) ON DELETE CASCADE;

-- Ensure control_structures table has proper constraints
ALTER TABLE control_structures 
DROP CONSTRAINT IF EXISTS control_structures_analysis_id_fkey;

ALTER TABLE control_structures 
ADD CONSTRAINT control_structures_analysis_id_fkey 
FOREIGN KEY (analysis_id) REFERENCES step2_analyses(id) ON DELETE CASCADE;

-- Create indexes for better performance on foreign key lookups
CREATE INDEX IF NOT EXISTS idx_input_analysis_analysis_id ON input_analysis(analysis_id);
CREATE INDEX IF NOT EXISTS idx_system_descriptions_analysis_id ON system_descriptions(analysis_id);

-- Add comments for clarity
COMMENT ON COLUMN input_analysis.analysis_id IS 'References either step1_analyses.id or step2_analyses.id depending on context';