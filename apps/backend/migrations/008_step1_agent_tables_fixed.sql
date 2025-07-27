-- Step 1 Agent Support Tables
-- Tables for agent activity logging and results storage

-- Agent activity log
CREATE TABLE IF NOT EXISTS agent_activity_log (
    id VARCHAR PRIMARY KEY,
    agent_type VARCHAR NOT NULL,
    analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
    activity VARCHAR NOT NULL,
    details JSONB,
    timestamp TIMESTAMP DEFAULT NOW()
);

-- Indexes for agent activity log
CREATE INDEX IF NOT EXISTS idx_agent_activity_analysis ON agent_activity_log(analysis_id);
CREATE INDEX IF NOT EXISTS idx_agent_activity_timestamp ON agent_activity_log(timestamp);

-- Agent results storage
CREATE TABLE IF NOT EXISTS agent_results (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
    agent_type VARCHAR NOT NULL,
    results JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    -- Ensure one result per agent per analysis
    UNIQUE (analysis_id, agent_type)
);

-- Indexes for agent results
CREATE INDEX IF NOT EXISTS idx_agent_results_analysis ON agent_results(analysis_id);
CREATE INDEX IF NOT EXISTS idx_agent_results_agent_type ON agent_results(agent_type);

-- Add metadata column to step1_analyses if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'step1_analyses' 
        AND column_name = 'metadata'
    ) THEN
        ALTER TABLE step1_analyses ADD COLUMN metadata JSONB;
    END IF;
END $$;

-- Add conditions column to hazard_loss_mappings if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'hazard_loss_mappings' 
        AND column_name = 'conditions'
    ) THEN
        ALTER TABLE hazard_loss_mappings ADD COLUMN conditions JSONB;
    END IF;
END $$;

-- Add architectural_hints and transition_guidance to step1_step2_bridge if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'step1_step2_bridge' 
        AND column_name = 'architectural_hints'
    ) THEN
        ALTER TABLE step1_step2_bridge 
        ADD COLUMN architectural_hints JSONB,
        ADD COLUMN transition_guidance JSONB;
    END IF;
END $$;

-- View for agent execution history
CREATE OR REPLACE VIEW agent_execution_summary AS
SELECT 
    a.id as analysis_id,
    a.name as analysis_name,
    COUNT(DISTINCT al.agent_type) as agents_executed,
    MIN(al.timestamp) as start_time,
    MAX(al.timestamp) as end_time,
    EXTRACT(EPOCH FROM (MAX(al.timestamp) - MIN(al.timestamp))) as duration_seconds,
    jsonb_agg(DISTINCT al.agent_type ORDER BY al.agent_type) as agent_types,
    COUNT(CASE WHEN al.activity LIKE '%error%' THEN 1 END) as error_count
FROM step1_analyses a
LEFT JOIN agent_activity_log al ON al.analysis_id = a.id
GROUP BY a.id, a.name;

-- View for agent result summary
CREATE OR REPLACE VIEW agent_result_summary AS
SELECT 
    ar.analysis_id,
    ar.agent_type,
    ar.created_at,
    jsonb_object_keys(ar.results) as result_keys,
    CASE 
        WHEN ar.results->>'status' = 'completed' THEN 'completed'
        WHEN ar.results->>'status' = 'error' THEN 'error'
        ELSE 'in_progress'
    END as status
FROM agent_results ar;

-- Function to get agent execution timeline
CREATE OR REPLACE FUNCTION get_agent_timeline(p_analysis_id VARCHAR)
RETURNS TABLE (
    agent_type VARCHAR,
    activity VARCHAR,
    timestamp TIMESTAMP,
    duration_to_next INTERVAL
) AS $$
BEGIN
    RETURN QUERY
    WITH timeline AS (
        SELECT 
            al.agent_type,
            al.activity,
            al.timestamp,
            LEAD(al.timestamp) OVER (ORDER BY al.timestamp) - al.timestamp as duration_to_next
        FROM agent_activity_log al
        WHERE al.analysis_id = p_analysis_id
        ORDER BY al.timestamp
    )
    SELECT * FROM timeline;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL ON agent_activity_log TO sa_user;
GRANT ALL ON agent_results TO sa_user;
GRANT SELECT ON agent_execution_summary TO sa_user;
GRANT SELECT ON agent_result_summary TO sa_user;
GRANT EXECUTE ON FUNCTION get_agent_timeline TO sa_user;