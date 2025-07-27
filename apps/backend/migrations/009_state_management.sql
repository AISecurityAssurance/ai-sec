-- State management for drafts and versions
-- This migration adds support for edit drafts, version tracking, and dependency analysis

-- Draft management for accumulating edits
CREATE TABLE analysis_drafts (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
    user_id VARCHAR NOT NULL,
    draft_data JSONB DEFAULT '{}',
    status VARCHAR CHECK (status IN ('working', 'committed', 'discarded')) DEFAULT 'working',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    committed_at TIMESTAMP,
    commit_version_id VARCHAR
);

-- Version tracking for analysis snapshots
CREATE TABLE analysis_versions (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    version_type VARCHAR CHECK (version_type IN ('auto_save', 'user_save', 'ai_generated')),
    state_snapshot JSONB NOT NULL,
    user_modifications JSONB DEFAULT '{}',
    commit_message TEXT,
    created_by VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    parent_version_id VARCHAR REFERENCES analysis_versions(id),
    UNIQUE(analysis_id, version_number)
);

-- Add foreign key for commit_version_id after table creation
ALTER TABLE analysis_drafts 
ADD CONSTRAINT fk_draft_version 
FOREIGN KEY (commit_version_id) 
REFERENCES analysis_versions(id);

-- Element dependency tracking for impact analysis
CREATE TABLE element_dependencies (
    source_type VARCHAR NOT NULL,
    source_id VARCHAR NOT NULL,
    dependent_type VARCHAR NOT NULL,
    dependent_id VARCHAR NOT NULL,
    dependency_strength VARCHAR CHECK (dependency_strength IN ('strong', 'moderate', 'weak')) DEFAULT 'strong',
    created_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (source_id, dependent_id)
);

-- Indexes for performance
CREATE INDEX idx_drafts_analysis_status ON analysis_drafts(analysis_id, status);
CREATE INDEX idx_drafts_user_working ON analysis_drafts(user_id, status) WHERE status = 'working';
CREATE INDEX idx_versions_analysis ON analysis_versions(analysis_id, version_number);
CREATE INDEX idx_dependencies_source ON element_dependencies(source_type, source_id);
CREATE INDEX idx_dependencies_dependent ON element_dependencies(dependent_type, dependent_id);

-- View for latest version per analysis
CREATE VIEW latest_analysis_versions AS
SELECT DISTINCT ON (analysis_id) 
    id,
    analysis_id,
    version_number,
    version_type,
    state_snapshot,
    user_modifications,
    created_by,
    created_at
FROM analysis_versions
ORDER BY analysis_id, version_number DESC;

-- View for active drafts
CREATE VIEW active_drafts AS
SELECT 
    d.*,
    a.name as analysis_name,
    a.system_type
FROM analysis_drafts d
JOIN step1_analyses a ON d.analysis_id = a.id
WHERE d.status = 'working';