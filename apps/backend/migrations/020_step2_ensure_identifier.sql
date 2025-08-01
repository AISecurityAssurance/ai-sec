-- Migration: 020_step2_ensure_identifier.sql
-- Description: Ensure identifier column exists in system_components
-- Created: 2025-01-31

-- Add identifier column if it doesn't exist
ALTER TABLE system_components ADD COLUMN IF NOT EXISTS identifier VARCHAR;

-- Update any NULL identifiers with generated values
UPDATE system_components 
SET identifier = CONCAT(
    CASE component_type 
        WHEN 'controller' THEN 'CTRL-'
        WHEN 'controlled_process' THEN 'PROC-'
        ELSE 'COMP-'
    END,
    SUBSTRING(id::text, 1, 8)
)
WHERE identifier IS NULL;

-- Make identifier NOT NULL after populating
ALTER TABLE system_components ALTER COLUMN identifier SET NOT NULL;

-- Add identifier columns to other tables if missing
ALTER TABLE control_actions ADD COLUMN IF NOT EXISTS identifier VARCHAR;
ALTER TABLE feedback_mechanisms ADD COLUMN IF NOT EXISTS identifier VARCHAR;
ALTER TABLE trust_boundaries ADD COLUMN IF NOT EXISTS identifier VARCHAR;

-- Update any NULL identifiers in other tables
UPDATE control_actions 
SET identifier = CONCAT('CA-', SUBSTRING(id::text, 1, 8))
WHERE identifier IS NULL;

UPDATE feedback_mechanisms
SET identifier = CONCAT('FB-', SUBSTRING(id::text, 1, 8))
WHERE identifier IS NULL;

UPDATE trust_boundaries
SET identifier = CONCAT('TB-', SUBSTRING(id::text, 1, 8))
WHERE identifier IS NULL;

-- Make identifiers NOT NULL
ALTER TABLE control_actions ALTER COLUMN identifier SET NOT NULL;
ALTER TABLE feedback_mechanisms ALTER COLUMN identifier SET NOT NULL;
ALTER TABLE trust_boundaries ALTER COLUMN identifier SET NOT NULL;