-- Migration 009: Add Security Constraints and System Boundaries for Step 1
-- This adds the missing components identified by security analysis review

-- Security Constraints table
CREATE TABLE security_constraints (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL,  -- SC-1, SC-2, etc.
    
    -- Constraint definition
    constraint_statement TEXT NOT NULL,  -- "The system shall..."
    rationale TEXT,  -- Why this constraint exists
    
    -- Classification
    constraint_type VARCHAR CHECK (constraint_type IN (
        'preventive',     -- Prevents hazard from occurring
        'detective',      -- Detects when hazard occurs
        'corrective',     -- Responds to hazard
        'compensating'    -- Reduces impact
    )),
    
    enforcement_level VARCHAR CHECK (enforcement_level IN (
        'mandatory',      -- SHALL - required for safety/security
        'recommended',    -- SHOULD - strong recommendation
        'optional'        -- MAY - good practice
    )),
    
    -- Mission context
    mission_impact_if_violated JSONB DEFAULT '{}',
    
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(analysis_id, identifier)
);

-- Many-to-many: constraints can address multiple hazards
CREATE TABLE constraint_hazard_mappings (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    constraint_id VARCHAR REFERENCES security_constraints(id) ON DELETE CASCADE,
    hazard_id VARCHAR REFERENCES step1_hazards(id) ON DELETE CASCADE,
    
    relationship_type VARCHAR CHECK (relationship_type IN (
        'eliminates',     -- Completely prevents the hazard
        'reduces',        -- Reduces likelihood or impact
        'detects',        -- Enables detection
        'transfers'       -- Shifts risk elsewhere
    )),
    
    effectiveness_rationale TEXT,
    
    UNIQUE(constraint_id, hazard_id)
);

-- System boundaries with multiple perspectives
CREATE TABLE system_boundaries (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
    
    boundary_name VARCHAR NOT NULL,
    boundary_type VARCHAR CHECK (boundary_type IN (
        'system_scope',      -- What's in/out of analysis
        'control',           -- Sphere of control
        'influence',         -- Sphere of influence  
        'responsibility',    -- Legal/regulatory boundary
        'trust',            -- Security trust boundary
        'data_governance'    -- Data ownership boundary
    )),
    
    description TEXT NOT NULL,
    
    -- Boundary definition
    definition_criteria JSONB DEFAULT '{}',  -- What defines this boundary
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- What's inside/outside/at the boundary
CREATE TABLE boundary_elements (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    boundary_id VARCHAR REFERENCES system_boundaries(id) ON DELETE CASCADE,
    
    element_name VARCHAR NOT NULL,
    element_type VARCHAR CHECK (element_type IN (
        'component',      -- System component
        'actor',          -- Human/system actor
        'data',           -- Data type/classification
        'process',        -- Business process
        'interface'       -- Connection point
    )),
    
    -- Position relative to boundary
    position VARCHAR CHECK (position IN (
        'inside',         -- Within boundary
        'outside',        -- External to boundary
        'crossing',       -- Spans boundary
        'interface'       -- At boundary interface
    )),
    
    -- Critical for analysis
    assumptions JSONB DEFAULT '{}',      -- What we assume about this element
    constraints JSONB DEFAULT '{}',      -- Limitations or requirements
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Relationships between boundaries (boundaries can overlap/nest)
CREATE TABLE boundary_relationships (
    id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::text,
    parent_boundary_id VARCHAR REFERENCES system_boundaries(id),
    child_boundary_id VARCHAR REFERENCES system_boundaries(id),
    relationship_type VARCHAR CHECK (relationship_type IN (
        'contains',       -- Parent contains child
        'overlaps',       -- Partial overlap
        'interfaces',     -- Touch at interface
        'delegates'       -- Parent delegates to child
    )),
    
    UNIQUE(parent_boundary_id, child_boundary_id)
);

-- Indexes for performance
CREATE INDEX idx_security_constraints_analysis ON security_constraints(analysis_id);
CREATE INDEX idx_constraint_hazard_constraint ON constraint_hazard_mappings(constraint_id);
CREATE INDEX idx_constraint_hazard_hazard ON constraint_hazard_mappings(hazard_id);
CREATE INDEX idx_system_boundaries_analysis ON system_boundaries(analysis_id);
CREATE INDEX idx_boundary_elements_boundary ON boundary_elements(boundary_id);

-- Views for analysis

-- Hazard constraint coverage view
CREATE VIEW hazard_constraint_coverage AS
SELECT 
    h.id as hazard_id,
    h.identifier as hazard,
    h.description as hazard_description,
    COUNT(DISTINCT chm.constraint_id) as constraint_count,
    BOOL_OR(chm.relationship_type = 'eliminates') as has_elimination,
    BOOL_OR(chm.relationship_type = 'detects') as has_detection,
    ARRAY_AGG(DISTINCT sc.identifier ORDER BY sc.identifier) as constraint_ids
FROM step1_hazards h
LEFT JOIN constraint_hazard_mappings chm ON h.id = chm.hazard_id
LEFT JOIN security_constraints sc ON chm.constraint_id = sc.id
GROUP BY h.id, h.identifier, h.description;

-- Boundary completeness view
CREATE VIEW boundary_completeness AS
SELECT 
    b.analysis_id,
    b.boundary_type,
    COUNT(DISTINCT b.id) as boundary_count,
    COUNT(DISTINCT be.id) as element_count,
    COUNT(DISTINCT CASE WHEN be.position = 'interface' THEN be.id END) as interface_count,
    COUNT(DISTINCT CASE WHEN be.position = 'inside' THEN be.id END) as internal_count,
    COUNT(DISTINCT CASE WHEN be.position = 'outside' THEN be.id END) as external_count
FROM system_boundaries b
LEFT JOIN boundary_elements be ON b.id = be.boundary_id
GROUP BY b.analysis_id, b.boundary_type;

-- Constraint effectiveness summary
CREATE VIEW constraint_effectiveness AS
SELECT 
    sc.id,
    sc.identifier,
    sc.constraint_statement,
    sc.constraint_type,
    sc.enforcement_level,
    COUNT(DISTINCT chm.hazard_id) as hazards_addressed,
    COUNT(DISTINCT CASE WHEN chm.relationship_type = 'eliminates' THEN chm.hazard_id END) as hazards_eliminated,
    COUNT(DISTINCT CASE WHEN chm.relationship_type = 'reduces' THEN chm.hazard_id END) as hazards_reduced,
    COUNT(DISTINCT CASE WHEN chm.relationship_type = 'detects' THEN chm.hazard_id END) as hazards_detected
FROM security_constraints sc
LEFT JOIN constraint_hazard_mappings chm ON sc.id = chm.constraint_id
GROUP BY sc.id, sc.identifier, sc.constraint_statement, sc.constraint_type, sc.enforcement_level;

-- Add tracking for these new components to step1_analyses
ALTER TABLE step1_analyses 
ADD COLUMN IF NOT EXISTS has_security_constraints BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS has_system_boundaries BOOLEAN DEFAULT FALSE;