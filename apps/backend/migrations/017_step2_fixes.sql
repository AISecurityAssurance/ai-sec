-- Migration: 017_step2_fixes.sql
-- Description: Fix Step 2 schema issues
-- Created: 2025-01-30

-- Add metadata column to step2_analyses if it doesn't exist
ALTER TABLE step2_analyses ADD COLUMN IF NOT EXISTS metadata JSONB;

-- Ensure all required columns exist in system_components
ALTER TABLE system_components ADD COLUMN IF NOT EXISTS identifier VARCHAR;

-- Add any missing indexes
CREATE INDEX IF NOT EXISTS idx_components_identifier ON system_components(analysis_id, identifier);