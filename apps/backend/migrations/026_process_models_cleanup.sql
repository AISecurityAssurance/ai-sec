-- Migration: 026_process_models_cleanup.sql
-- Description: Clean up process_models table structure inconsistencies
-- Created: 2025-08-02

-- The original migration 016 created process_models with model_name as NOT NULL,
-- but the ProcessModelAnalyst doesn't use this field. We need to either:
-- 1. Drop the NOT NULL constraint, or
-- 2. Drop the column entirely if it's not used

-- First, check if model_name column exists and drop NOT NULL constraint if it does
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'process_models' AND column_name = 'model_name'
    ) THEN
        -- Drop NOT NULL constraint
        ALTER TABLE process_models ALTER COLUMN model_name DROP NOT NULL;
        
        -- Set a default value for existing NULL entries
        UPDATE process_models SET model_name = 'Process Model ' || COALESCE(identifier, id) WHERE model_name IS NULL;
    END IF;
END $$;

-- Also ensure that the inadequate_control_scenarios table is properly set up for Step 3
-- (it shouldn't be populated in Step 2)
COMMENT ON TABLE inadequate_control_scenarios IS 'Step 3: Identifies scenarios where control is inadequate - NOT populated in Step 2';