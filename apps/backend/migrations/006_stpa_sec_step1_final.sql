-- Migration: 006_stpa_sec_step1_final.sql
-- Description: Final STPA-Sec Step 1 schema with proper abstractions
-- Created: 2024-01-27

-- =====================================================
-- STEP 0: CREATE ANALYSIS CONTAINER TABLE
-- =====================================================

-- Create a table for Step 1 analyses (different from existing stpa_analyses)
CREATE TABLE IF NOT EXISTS step1_analyses (
  id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  description TEXT,
  system_type VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR
);

-- =====================================================
-- STEP 1: PROBLEM FRAMING TABLES
-- =====================================================

-- 1. Problem Statement with structured components
CREATE TABLE IF NOT EXISTS problem_statements (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  -- Structured components for validation and composition
  purpose_what TEXT NOT NULL,
  method_how TEXT NOT NULL,  
  goals_why TEXT NOT NULL,
  
  -- Generated full statement for readability
  full_statement TEXT GENERATED ALWAYS AS (
    'A System to ' || purpose_what || 
    ' by means of ' || method_how || 
    ' in order to ' || goals_why
  ) STORED,
  
  -- Mission context
  mission_context JSONB DEFAULT '{}',
  
  -- Operational constraints and assumptions  
  operational_constraints JSONB DEFAULT '{}',
  environmental_assumptions JSONB DEFAULT '{}',
  
  -- Analysis confidence (metadata about our understanding)
  analysis_confidence JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Losses with proper categorization
CREATE TABLE IF NOT EXISTS step1_losses (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  identifier VARCHAR NOT NULL, -- L1, L2, etc.
  description TEXT NOT NULL,
  loss_category VARCHAR NOT NULL CHECK (loss_category IN (
    'life', 'injury', 'financial', 'environmental', 
    'mission', 'reputation', 'privacy', 'regulatory'
  )),
  
  -- Severity classification
  severity_classification JSONB DEFAULT '{}',
  
  -- Mission impact
  mission_impact JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  -- Ensure unique identifiers per analysis
  UNIQUE(analysis_id, identifier)
);

-- 3. Loss Dependencies for cascade analysis
CREATE TABLE IF NOT EXISTS loss_dependencies (
  id VARCHAR PRIMARY KEY,
  primary_loss_id VARCHAR NOT NULL REFERENCES step1_losses(id) ON DELETE CASCADE,
  dependent_loss_id VARCHAR NOT NULL REFERENCES step1_losses(id) ON DELETE CASCADE,
  
  dependency_type VARCHAR NOT NULL CHECK (dependency_type IN (
    'enables',      -- Primary loss makes dependent loss possible
    'amplifies',    -- Primary loss increases dependent loss severity
    'triggers'      -- Primary loss directly causes dependent loss
  )),
  
  dependency_strength VARCHAR NOT NULL CHECK (dependency_strength IN (
    'certain',      -- Will definitely occur
    'likely',       -- High probability
    'possible'      -- Could occur under certain conditions
  )),
  
  -- Time relationship (abstract, not mechanistic)
  time_relationship JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  -- Prevent circular dependencies and duplicates
  UNIQUE(primary_loss_id, dependent_loss_id),
  CHECK(primary_loss_id != dependent_loss_id)
);

-- 4. Hazards as system states
CREATE TABLE IF NOT EXISTS step1_hazards (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  identifier VARCHAR NOT NULL, -- H1, H2, etc.
  description TEXT NOT NULL,
  
  hazard_category VARCHAR NOT NULL CHECK (hazard_category IN (
    'integrity_compromised', 'availability_degraded', 
    'confidentiality_breached', 'non_compliance', 
    'mission_degraded', 'capability_loss'
  )),
  
  affected_system_property VARCHAR CHECK (affected_system_property IN (
    'transaction_integrity', 'data_protection', 'service_availability',
    'regulatory_compliance', 'operational_capability', 'mission_effectiveness'
  )),
  
  -- Environmental factors
  environmental_factors JSONB DEFAULT '{}',
  
  -- Temporal nature (when this state can exist)
  temporal_nature JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  -- Ensure unique identifiers per analysis
  UNIQUE(analysis_id, identifier)
);

-- 5. Hazard-Loss Mappings
CREATE TABLE IF NOT EXISTS hazard_loss_mappings (
  id VARCHAR PRIMARY KEY,
  hazard_id VARCHAR NOT NULL REFERENCES step1_hazards(id) ON DELETE CASCADE,
  loss_id VARCHAR NOT NULL REFERENCES step1_losses(id) ON DELETE CASCADE,
  
  -- Simple relationship type
  relationship_strength VARCHAR CHECK (relationship_strength IN (
    'direct', 'indirect', 'conditional'
  )),
  
  -- Brief rationale (no implementation details)
  rationale TEXT,
  
  created_at TIMESTAMP DEFAULT NOW(),
  
  -- Prevent duplicate mappings
  UNIQUE(hazard_id, loss_id)
);

-- 6. Stakeholders (non-adversary)
CREATE TABLE IF NOT EXISTS step1_stakeholders (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  name VARCHAR NOT NULL,
  stakeholder_type VARCHAR NOT NULL CHECK (stakeholder_type IN (
    'user', 'operator', 'owner', 'regulator', 
    'partner', 'society', 'supplier'
  )),
  
  -- What success and failure mean to them
  mission_perspective JSONB DEFAULT '{}',
  
  -- Which losses directly affect them
  loss_exposure JSONB DEFAULT '{}',
  
  -- Influence and interest
  influence_interest JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- 7. Adversary Profiles (separate from stakeholders)
CREATE TABLE IF NOT EXISTS adversary_profiles (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  adversary_class VARCHAR NOT NULL CHECK (adversary_class IN (
    'nation_state', 'organized_crime', 'hacktivist', 
    'insider', 'competitor', 'opportunist'
  )),
  
  -- High-level profile
  profile JSONB DEFAULT '{}',
  
  -- What they target (abstract, not technical)
  mission_targets JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- 8. Mission Success Criteria
CREATE TABLE IF NOT EXISTS mission_success_criteria (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  -- What success looks like to stakeholders
  success_states JSONB DEFAULT '{}',
  
  -- Observable indicators (what success looks like, not how achieved)
  success_indicators JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- 9. Step 1 to Step 2 Bridge
CREATE TABLE IF NOT EXISTS step1_step2_bridge (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  -- Abstract control needs derived from hazards (what, not how)
  control_needs JSONB DEFAULT '{}',
  
  -- Key interaction points implied by stakeholder analysis
  implied_boundaries JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- 10. Problem Framing Versions for iteration tracking
CREATE TABLE IF NOT EXISTS problem_framing_versions (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  version_number INTEGER NOT NULL,
  version_tag VARCHAR, -- "initial", "post_review", "final", etc.
  
  -- Change tracking
  changes JSONB DEFAULT '{}',
  
  -- Complete snapshot at this version
  problem_statement_snapshot JSONB,
  losses_snapshot JSONB,
  hazards_snapshot JSONB,
  stakeholders_snapshot JSONB,
  
  -- Review and approval
  review_notes TEXT,
  approved_by VARCHAR,
  approval_date TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR,
  
  -- Ensure unique version numbers per analysis
  UNIQUE(analysis_id, version_number)
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Analysis lookups
CREATE INDEX idx_problem_statements_analysis ON problem_statements(analysis_id);
CREATE INDEX idx_losses_analysis ON step1_losses(analysis_id);
CREATE INDEX idx_hazards_analysis ON step1_hazards(analysis_id);
CREATE INDEX idx_stakeholders_analysis ON step1_stakeholders(analysis_id);
CREATE INDEX idx_adversary_profiles_analysis ON adversary_profiles(analysis_id);

-- Identifier lookups
CREATE INDEX idx_losses_identifier ON step1_losses(analysis_id, identifier);
CREATE INDEX idx_hazards_identifier ON step1_hazards(analysis_id, identifier);

-- Relationship lookups
CREATE INDEX idx_loss_dependencies_primary ON loss_dependencies(primary_loss_id);
CREATE INDEX idx_loss_dependencies_dependent ON loss_dependencies(dependent_loss_id);
CREATE INDEX idx_hazard_loss_mappings_hazard ON hazard_loss_mappings(hazard_id);
CREATE INDEX idx_hazard_loss_mappings_loss ON hazard_loss_mappings(loss_id);

-- JSONB indexes for common queries
CREATE INDEX idx_stakeholders_influence ON step1_stakeholders USING GIN ((influence_interest->'influence_level'));
CREATE INDEX idx_losses_severity ON step1_losses USING GIN ((severity_classification->'magnitude'));

-- =====================================================
-- VIEWS FOR ANALYSIS
-- =====================================================

-- 1. Comprehensive Problem Framing Status
CREATE VIEW problem_framing_completeness AS
SELECT 
  ps.analysis_id,
  ps.full_statement,
  
  -- Element counts
  COUNT(DISTINCT l.id) as loss_count,
  COUNT(DISTINCT h.id) as hazard_count,
  COUNT(DISTINCT s.id) as stakeholder_count,
  COUNT(DISTINCT ap.id) as adversary_count,
  
  -- Coverage analysis
  COUNT(DISTINCT hlm.loss_id) as losses_with_hazards,
  COUNT(DISTINCT l.id) - COUNT(DISTINCT hlm.loss_id) as uncovered_losses,
  
  -- Completeness score
  CASE 
    WHEN ps.purpose_what IS NOT NULL 
     AND ps.method_how IS NOT NULL 
     AND ps.goals_why IS NOT NULL
     AND COUNT(DISTINCT l.id) >= 3
     AND COUNT(DISTINCT h.id) >= 3
     AND COUNT(DISTINCT s.id) >= 3
     AND COUNT(DISTINCT ap.id) >= 1
     AND COUNT(DISTINCT hlm.loss_id) = COUNT(DISTINCT l.id)
    THEN 'comprehensive'
    WHEN COUNT(DISTINCT l.id) > 0 
     AND COUNT(DISTINCT h.id) > 0
    THEN 'adequate'
    ELSE 'incomplete'
  END as completeness_level

FROM problem_statements ps
LEFT JOIN step1_losses l ON ps.analysis_id = l.analysis_id
LEFT JOIN step1_hazards h ON ps.analysis_id = h.analysis_id
LEFT JOIN hazard_loss_mappings hlm ON l.id = hlm.loss_id
LEFT JOIN step1_stakeholders s ON ps.analysis_id = s.analysis_id
LEFT JOIN adversary_profiles ap ON ps.analysis_id = ap.analysis_id
GROUP BY ps.analysis_id, ps.full_statement, ps.purpose_what, ps.method_how, ps.goals_why;

-- 2. Stakeholder Loss Sensitivity Matrix
CREATE VIEW stakeholder_loss_matrix AS
SELECT 
  s.name as stakeholder,
  s.stakeholder_type,
  l.identifier as loss_id,
  l.description as loss_description,
  
  -- Extract sensitivity from JSON
  s.loss_exposure->'severity_perception'->>l.identifier as sensitivity_level,
  
  -- Determine engagement priority
  CASE 
    WHEN s.loss_exposure->'severity_perception'->>l.identifier = 'catastrophic' 
     AND s.influence_interest->>'influence_level' = 'high'
    THEN 'critical_engagement'
    WHEN s.loss_exposure->'severity_perception'->>l.identifier IN ('catastrophic', 'major')
    THEN 'high_priority'
    ELSE 'standard'
  END as engagement_priority

FROM step1_stakeholders s
CROSS JOIN step1_losses l
WHERE s.analysis_id = l.analysis_id
  AND s.loss_exposure->'severity_perception' ? l.identifier
ORDER BY 
  CASE s.loss_exposure->'severity_perception'->>l.identifier
    WHEN 'catastrophic' THEN 1
    WHEN 'major' THEN 2
    WHEN 'moderate' THEN 3
    WHEN 'minor' THEN 4
  END,
  s.name;

-- 3. Environmental Risk Context View
CREATE VIEW environmental_risk_context AS
SELECT 
  h.identifier as hazard_id,
  h.description as hazard_description,
  
  -- Aggregate environmental risk
  GREATEST(
    CASE h.environmental_factors->'operational_conditions'->'emergency'->>'impact'
      WHEN 'catastrophic' THEN 5
      WHEN 'high' THEN 4
      WHEN 'moderate' THEN 3
      WHEN 'low' THEN 2
      ELSE 1
    END,
    CASE h.environmental_factors->'threat_conditions'->'severe'->>'system_resilience'
      WHEN 'overwhelmed' THEN 5
      WHEN 'stressed' THEN 3
      WHEN 'adequate' THEN 1
      ELSE 1
    END
  ) as environmental_risk_score,
  
  -- Temporal vulnerability
  h.temporal_nature as temporal_pattern,
  
  -- Associated losses and their severity
  STRING_AGG(
    l.identifier || ' (' || 
    COALESCE(l.severity_classification->>'magnitude', 'unspecified') || ')', 
    ', '
  ) as affected_losses

FROM step1_hazards h
JOIN hazard_loss_mappings hlm ON h.id = hlm.hazard_id
JOIN step1_losses l ON hlm.loss_id = l.id
GROUP BY h.id, h.identifier, h.description, h.environmental_factors, h.temporal_nature;

-- 4. Loss Cascade Chains (Recursive CTE)
CREATE VIEW loss_cascade_chains AS
WITH RECURSIVE loss_chains AS (
    -- Base case: primary losses
    SELECT 
        id as chain_start,
        id as current_loss,
        identifier as chain_path,
        0 as depth
    FROM step1_losses
    
    UNION ALL
    
    -- Recursive case: follow dependencies
    SELECT
        lc.chain_start,
        ld.dependent_loss_id,
        lc.chain_path || ' → ' || l.identifier,
        lc.depth + 1
    FROM loss_chains lc
    JOIN loss_dependencies ld ON lc.current_loss = ld.primary_loss_id
    JOIN step1_losses l ON ld.dependent_loss_id = l.id
    WHERE lc.depth < 5  -- Prevent infinite loops
)
SELECT 
    lc.chain_start,
    lc.chain_path,
    lc.depth,
    l.description as starting_loss_desc,
    l.severity_classification->>'magnitude' as starting_severity
FROM loss_chains lc
JOIN step1_losses l ON lc.chain_start = l.id
WHERE lc.depth > 0 
ORDER BY lc.chain_start, lc.depth;

-- 5. Temporal Hazard Windows
CREATE VIEW temporal_hazard_exposure AS
SELECT 
  h.identifier,
  h.description,
  h.temporal_nature->>'existence' as temporal_pattern,
  h.temporal_nature->>'when_present' as vulnerability_window,
  
  -- Which losses could occur during these windows
  STRING_AGG(l.identifier, ', ' ORDER BY l.identifier) as exposed_losses

FROM step1_hazards h
JOIN hazard_loss_mappings hlm ON h.id = hlm.hazard_id
JOIN step1_losses l ON hlm.loss_id = l.id
WHERE h.temporal_nature->>'existence' != 'always'
  AND h.temporal_nature->>'existence' IS NOT NULL
GROUP BY h.id, h.identifier, h.description, h.temporal_nature;

-- 6. Success State Violation Analysis
CREATE VIEW success_violation_analysis AS
SELECT 
  msc.analysis_id,
  
  -- Extract each success state
  jsonb_object_keys(msc.success_states) as success_dimension,
  
  -- Get the description and violated_by_losses for each state
  msc.success_states->jsonb_object_keys(msc.success_states)->>'description' as success_description,
  msc.success_states->jsonb_object_keys(msc.success_states)->>'violated_by_losses' as violating_losses

FROM mission_success_criteria msc
WHERE msc.success_states IS NOT NULL;

-- 7. Executive Summary View
CREATE VIEW step1_executive_summary AS
SELECT
  ps.analysis_id,
  
  -- Executive summary
  'This analysis examines ' || ps.purpose_what ||
  ' achieved through ' || ps.method_how ||
  ' to ' || ps.goals_why as executive_summary,
  
  -- Key risks (top 5 by severity)
  (
    SELECT STRING_AGG(
      sub.identifier || ': ' || sub.description,
      E'\n'
      ORDER BY sub.severity_order
    )
    FROM (
      SELECT 
        l.identifier,
        l.description,
        CASE l.severity_classification->>'magnitude'
          WHEN 'catastrophic' THEN 1
          WHEN 'major' THEN 2
          WHEN 'moderate' THEN 3
          ELSE 4
        END as severity_order
      FROM losses l
      WHERE l.analysis_id = ps.analysis_id
      ORDER BY severity_order
      LIMIT 5
    ) sub
  ) as top_risks,
  
  -- Critical system states
  (
    SELECT STRING_AGG(
      h.identifier || ': ' || h.description,
      E'\n'
      ORDER BY h.identifier
    )
    FROM hazards h
    WHERE h.analysis_id = ps.analysis_id
      AND h.hazard_category IN ('integrity_compromised', 'mission_degraded')
  ) as critical_system_states,
  
  -- Stakeholder summary
  (SELECT COUNT(*) FROM stakeholders s WHERE s.analysis_id = ps.analysis_id) as stakeholder_count,
  (SELECT COUNT(*) FROM adversary_profiles ap WHERE ap.analysis_id = ps.analysis_id) as adversary_count

FROM problem_statements ps;

-- =====================================================
-- VALIDATION FUNCTIONS
-- =====================================================

-- Function to check if an analysis has all required Step 1 elements
CREATE OR REPLACE FUNCTION validate_step1_completeness(p_analysis_id VARCHAR)
RETURNS TABLE(
  element VARCHAR,
  status VARCHAR,
  details TEXT
) AS $$
BEGIN
  -- Check problem statement
  RETURN QUERY
  SELECT 
    'problem_statement'::VARCHAR,
    CASE WHEN COUNT(*) > 0 THEN 'complete'::VARCHAR ELSE 'missing'::VARCHAR END,
    CASE WHEN COUNT(*) > 0 THEN 'Problem statement defined'::TEXT 
         ELSE 'No problem statement found'::TEXT END
  FROM problem_statements
  WHERE analysis_id = p_analysis_id;
  
  -- Check losses
  RETURN QUERY
  SELECT 
    'losses'::VARCHAR,
    CASE WHEN COUNT(*) >= 3 THEN 'complete'::VARCHAR 
         WHEN COUNT(*) > 0 THEN 'partial'::VARCHAR 
         ELSE 'missing'::VARCHAR END,
    'Found ' || COUNT(*) || ' losses (minimum 3 recommended)'::TEXT
  FROM losses
  WHERE analysis_id = p_analysis_id;
  
  -- Check hazards
  RETURN QUERY
  SELECT 
    'hazards'::VARCHAR,
    CASE WHEN COUNT(*) >= 3 THEN 'complete'::VARCHAR 
         WHEN COUNT(*) > 0 THEN 'partial'::VARCHAR 
         ELSE 'missing'::VARCHAR END,
    'Found ' || COUNT(*) || ' hazards (minimum 3 recommended)'::TEXT
  FROM hazards
  WHERE analysis_id = p_analysis_id;
  
  -- Check hazard-loss coverage
  RETURN QUERY
  WITH coverage AS (
    SELECT 
      COUNT(DISTINCT l.id) as total_losses,
      COUNT(DISTINCT hlm.loss_id) as covered_losses
    FROM losses l
    LEFT JOIN hazard_loss_mappings hlm ON l.id = hlm.loss_id
    WHERE l.analysis_id = p_analysis_id
  )
  SELECT 
    'hazard_loss_coverage'::VARCHAR,
    CASE WHEN covered_losses = total_losses AND total_losses > 0 THEN 'complete'::VARCHAR
         WHEN covered_losses > 0 THEN 'partial'::VARCHAR
         ELSE 'missing'::VARCHAR END,
    covered_losses || ' of ' || total_losses || ' losses have hazard mappings'::TEXT
  FROM coverage;
  
  -- Check stakeholders
  RETURN QUERY
  SELECT 
    'stakeholders'::VARCHAR,
    CASE WHEN COUNT(*) >= 3 THEN 'complete'::VARCHAR 
         WHEN COUNT(*) > 0 THEN 'partial'::VARCHAR 
         ELSE 'missing'::VARCHAR END,
    'Found ' || COUNT(*) || ' stakeholders'::TEXT
  FROM stakeholders
  WHERE analysis_id = p_analysis_id;
  
  -- Check adversaries
  RETURN QUERY
  SELECT 
    'adversaries'::VARCHAR,
    CASE WHEN COUNT(*) >= 1 THEN 'complete'::VARCHAR 
         ELSE 'missing'::VARCHAR END,
    'Found ' || COUNT(*) || ' adversary profiles'::TEXT
  FROM adversary_profiles
  WHERE analysis_id = p_analysis_id;
  
  -- Check mission success criteria
  RETURN QUERY
  SELECT 
    'success_criteria'::VARCHAR,
    CASE WHEN COUNT(*) > 0 THEN 'complete'::VARCHAR ELSE 'missing'::VARCHAR END,
    CASE WHEN COUNT(*) > 0 THEN 'Mission success criteria defined'::TEXT 
         ELSE 'No success criteria found'::TEXT END
  FROM mission_success_criteria
  WHERE analysis_id = p_analysis_id;
  
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- MIGRATION COMPLETION
-- =====================================================

-- Add comment to track schema version
COMMENT ON SCHEMA public IS 'STPA-Sec Step 1 Final Schema v1.0';