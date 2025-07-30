-- Migration: 014_input_analysis_table.sql
-- Description: Add input_analysis table for storing Input Agent results
-- Created: 2025-01-30

-- =====================================================
-- CREATE INPUT ANALYSIS TABLE
-- =====================================================

-- Input Analysis table for storing results from the Input Agent
CREATE TABLE IF NOT EXISTS input_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL,
    input_name TEXT NOT NULL,
    input_type TEXT NOT NULL,
    input_path TEXT,
    summary TEXT,  -- Changed from content_summary to match expected column name
    confidence DECIMAL(3,2),
    metadata JSONB DEFAULT '{}',
    assumptions TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_input_analysis_analysis_id ON input_analysis(analysis_id);

-- Grant permissions
GRANT ALL ON input_analysis TO sa_user;

-- Add comment
COMMENT ON TABLE input_analysis IS 'Stores analysis results from the Input Agent for each processed input';