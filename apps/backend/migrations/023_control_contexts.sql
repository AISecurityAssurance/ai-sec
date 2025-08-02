-- Migration: Add control context tables for Step 2
-- This replaces the state_context tables which included unsafe state analysis

-- Control contexts table (replaces enhanced_control_contexts)
CREATE TABLE IF NOT EXISTS control_contexts (
    id UUID PRIMARY KEY,
    analysis_id VARCHAR NOT NULL REFERENCES step2_analyses(id) ON DELETE CASCADE,
    control_action_id VARCHAR REFERENCES control_actions(id),
    
    -- Execution context
    execution_context JSONB,  -- triggers, preconditions, environmental factors, timing
    
    -- Decision logic
    decision_logic JSONB,  -- inputs evaluated, criteria, priority, conflict resolution
    
    -- Valid modes
    valid_modes TEXT[],
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure one context per control action per analysis
    UNIQUE(analysis_id, control_action_id)
);

-- Operational modes table
CREATE TABLE IF NOT EXISTS operational_modes (
    id UUID PRIMARY KEY,
    analysis_id VARCHAR NOT NULL REFERENCES step2_analyses(id) ON DELETE CASCADE,
    
    mode_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Mode conditions
    entry_conditions TEXT[],
    exit_conditions TEXT[],
    
    -- Active components in this mode
    active_controllers TEXT[],
    available_actions TEXT[],
    
    -- Constraints
    mode_constraints TEXT[],
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Ensure unique mode names per analysis
    UNIQUE(analysis_id, mode_name)
);

-- Mode transitions table
CREATE TABLE IF NOT EXISTS mode_transitions (
    id UUID PRIMARY KEY,
    analysis_id VARCHAR NOT NULL REFERENCES step2_analyses(id) ON DELETE CASCADE,
    
    from_mode VARCHAR(255),
    to_mode VARCHAR(255),
    transition_trigger TEXT,
    transition_actions TEXT[],
    transition_time VARCHAR(100),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_control_contexts_analysis ON control_contexts(analysis_id);
CREATE INDEX idx_control_contexts_action ON control_contexts(control_action_id);
CREATE INDEX idx_operational_modes_analysis ON operational_modes(analysis_id);
CREATE INDEX idx_mode_transitions_analysis ON mode_transitions(analysis_id);