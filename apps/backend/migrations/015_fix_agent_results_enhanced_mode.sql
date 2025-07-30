-- Migration: 015_fix_agent_results_enhanced_mode.sql
-- Description: Fix agent_results table to support enhanced mode with multiple cognitive styles
-- Created: 2025-01-30

-- =====================================================
-- FIX AGENT RESULTS TABLE FOR ENHANCED MODE
-- =====================================================

-- Drop the existing unique constraint that prevents multiple results per agent type
ALTER TABLE agent_results DROP CONSTRAINT IF EXISTS agent_results_analysis_id_agent_type_key;

-- Add cognitive_style column to differentiate results from different perspectives
ALTER TABLE agent_results ADD COLUMN IF NOT EXISTS cognitive_style VARCHAR DEFAULT 'standard';

-- Create new unique constraint that allows multiple results per agent type with different cognitive styles
ALTER TABLE agent_results ADD CONSTRAINT agent_results_unique_per_style 
    UNIQUE (analysis_id, agent_type, cognitive_style);

-- Update existing records to have a cognitive_style
UPDATE agent_results SET cognitive_style = 'standard' WHERE cognitive_style IS NULL;

-- Add comment
COMMENT ON COLUMN agent_results.cognitive_style IS 'Cognitive style used by the agent (standard, intuitive, analytical, etc.)';