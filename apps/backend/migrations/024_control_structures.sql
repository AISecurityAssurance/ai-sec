-- Migration: Add control_structures table for Step 2
-- This table stores the control structure analysis results

CREATE TABLE IF NOT EXISTS control_structures (
    id UUID PRIMARY KEY,
    analysis_id VARCHAR NOT NULL REFERENCES step2_analyses(id) ON DELETE CASCADE,
    
    -- Control structure description
    description TEXT,
    
    -- Components (JSONB for flexibility)
    components JSONB,  -- controllers, controlled_processes, feedback_loops
    
    -- Hierarchy (JSONB)
    hierarchy JSONB,  -- levels, relationships
    
    -- Metadata
    execution_mode VARCHAR(50),
    cognitive_style VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure one control structure per analysis
    UNIQUE(analysis_id)
);

-- Index for fast lookups
CREATE INDEX idx_control_structures_analysis ON control_structures(analysis_id);