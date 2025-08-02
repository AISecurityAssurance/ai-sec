-- Migration: Add system description table for Step 1
-- This table stores comprehensive system descriptions generated in Step 1
-- to serve as primary input for Step 2 control structure analysis

CREATE TABLE IF NOT EXISTS system_descriptions (
    id UUID PRIMARY KEY,
    analysis_id VARCHAR NOT NULL REFERENCES step1_analyses(id) ON DELETE CASCADE,
    
    -- System overview
    system_name VARCHAR(255) NOT NULL,
    system_type VARCHAR(100),
    purpose TEXT,
    scope TEXT,
    operational_context TEXT,
    
    -- Architecture (stored as JSONB for flexibility)
    architecture JSONB,
    
    -- Components (array of component objects)
    components JSONB,
    
    -- Interactions (array of interaction objects)
    interactions JSONB,
    
    -- Control hierarchy
    control_hierarchy JSONB,
    
    -- Operational flows (array of flow objects)
    operational_flows JSONB,
    
    -- Key characteristics
    key_characteristics JSONB,
    
    -- Metadata
    description_version VARCHAR(10) DEFAULT '1.0',
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Full raw response for reference
    raw_data JSONB
);

-- Index for fast lookups by analysis
CREATE INDEX idx_system_descriptions_analysis_id ON system_descriptions(analysis_id);

-- Add system_description_id to step1_analyses for easy reference
ALTER TABLE step1_analyses ADD COLUMN IF NOT EXISTS system_description_id UUID;

-- Add foreign key constraint
ALTER TABLE step1_analyses 
ADD CONSTRAINT fk_system_description 
FOREIGN KEY (system_description_id) 
REFERENCES system_descriptions(id);