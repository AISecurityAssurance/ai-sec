-- Migration: 007_stpa_sec_step1_clean.sql
-- Description: STPA-Sec Step 1 schema with prefixed table names to avoid conflicts
-- Created: 2024-01-27

-- =====================================================
-- DROP EXISTING OBJECTS IF THEY EXIST
-- =====================================================

DROP VIEW IF EXISTS problem_framing_completeness CASCADE;
DROP VIEW IF EXISTS stakeholder_loss_matrix CASCADE;
DROP VIEW IF EXISTS environmental_risk_context CASCADE;
DROP VIEW IF EXISTS loss_cascade_chains CASCADE;
DROP VIEW IF EXISTS temporal_hazard_exposure CASCADE;
DROP VIEW IF EXISTS success_violation_analysis CASCADE;
DROP VIEW IF EXISTS step1_executive_summary CASCADE;

DROP FUNCTION IF EXISTS validate_step1_completeness(VARCHAR);

DROP TABLE IF EXISTS problem_framing_versions CASCADE;
DROP TABLE IF EXISTS step1_step2_bridge CASCADE;
DROP TABLE IF EXISTS mission_success_criteria CASCADE;
DROP TABLE IF EXISTS adversary_profiles CASCADE;
DROP TABLE IF EXISTS step1_stakeholders CASCADE;
DROP TABLE IF EXISTS hazard_loss_mappings CASCADE;
DROP TABLE IF EXISTS step1_hazards CASCADE;
DROP TABLE IF EXISTS loss_dependencies CASCADE;
DROP TABLE IF EXISTS step1_losses CASCADE;
DROP TABLE IF EXISTS problem_statements CASCADE;
DROP TABLE IF EXISTS step1_analyses CASCADE;

-- =====================================================
-- CREATE TABLES WITH STEP1_ PREFIX
-- =====================================================

-- Analysis container
CREATE TABLE step1_analyses (
  id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  description TEXT,
  system_type VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR
);

-- Problem Statement
CREATE TABLE problem_statements (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  purpose_what TEXT NOT NULL,
  method_how TEXT NOT NULL,  
  goals_why TEXT NOT NULL,
  
  full_statement TEXT GENERATED ALWAYS AS (
    'A System to ' || purpose_what || 
    ' by means of ' || method_how || 
    ' in order to ' || goals_why
  ) STORED,
  
  mission_context JSONB DEFAULT '{}',
  operational_constraints JSONB DEFAULT '{}',
  environmental_assumptions JSONB DEFAULT '{}',
  analysis_confidence JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Losses
CREATE TABLE step1_losses (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  identifier VARCHAR NOT NULL,
  description TEXT NOT NULL,
  loss_category VARCHAR NOT NULL CHECK (loss_category IN (
    'life', 'injury', 'financial', 'environmental', 
    'mission', 'reputation', 'privacy', 'regulatory'
  )),
  
  severity_classification JSONB DEFAULT '{}',
  mission_impact JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(analysis_id, identifier)
);

-- Loss Dependencies
CREATE TABLE loss_dependencies (
  id VARCHAR PRIMARY KEY,
  primary_loss_id VARCHAR NOT NULL REFERENCES step1_losses(id) ON DELETE CASCADE,
  dependent_loss_id VARCHAR NOT NULL REFERENCES step1_losses(id) ON DELETE CASCADE,
  
  dependency_type VARCHAR NOT NULL CHECK (dependency_type IN (
    'enables', 'amplifies', 'triggers'
  )),
  
  dependency_strength VARCHAR NOT NULL CHECK (dependency_strength IN (
    'certain', 'likely', 'possible'
  )),
  
  time_relationship JSONB DEFAULT '{}',
  rationale TEXT,
  
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(primary_loss_id, dependent_loss_id),
  CHECK(primary_loss_id != dependent_loss_id)
);

-- Hazards
CREATE TABLE step1_hazards (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  identifier VARCHAR NOT NULL,
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
  
  environmental_factors JSONB DEFAULT '{}',
  temporal_nature JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(analysis_id, identifier)
);

-- Hazard-Loss Mappings
CREATE TABLE hazard_loss_mappings (
  id VARCHAR PRIMARY KEY,
  hazard_id VARCHAR NOT NULL REFERENCES step1_hazards(id) ON DELETE CASCADE,
  loss_id VARCHAR NOT NULL REFERENCES step1_losses(id) ON DELETE CASCADE,
  
  relationship_strength VARCHAR CHECK (relationship_strength IN (
    'direct', 'indirect', 'conditional'
  )),
  
  rationale TEXT,
  
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(hazard_id, loss_id)
);

-- Stakeholders (non-adversary)
CREATE TABLE step1_stakeholders (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  name VARCHAR NOT NULL,
  stakeholder_type VARCHAR NOT NULL CHECK (stakeholder_type IN (
    'user', 'operator', 'owner', 'regulator', 
    'partner', 'society', 'supplier'
  )),
  
  mission_perspective JSONB DEFAULT '{}',
  loss_exposure JSONB DEFAULT '{}',
  influence_interest JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Adversary Profiles
CREATE TABLE adversary_profiles (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  adversary_class VARCHAR NOT NULL CHECK (adversary_class IN (
    'nation_state', 'organized_crime', 'hacktivist', 
    'insider', 'competitor', 'opportunist'
  )),
  
  profile JSONB DEFAULT '{}',
  mission_targets JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Mission Success Criteria
CREATE TABLE mission_success_criteria (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  success_states JSONB DEFAULT '{}',
  success_indicators JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Step 1 to Step 2 Bridge
CREATE TABLE step1_step2_bridge (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  
  control_needs JSONB DEFAULT '{}',
  implied_boundaries JSONB DEFAULT '{}',
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Problem Framing Versions
CREATE TABLE problem_framing_versions (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
  version_number INTEGER NOT NULL,
  version_tag VARCHAR,
  
  changes JSONB DEFAULT '{}',
  
  problem_statement_snapshot JSONB,
  losses_snapshot JSONB,
  hazards_snapshot JSONB,
  stakeholders_snapshot JSONB,
  
  review_notes TEXT,
  approved_by VARCHAR,
  approval_date TIMESTAMP,
  
  created_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR,
  
  UNIQUE(analysis_id, version_number)
);

-- =====================================================
-- INDEXES
-- =====================================================

CREATE INDEX idx_problem_statements_analysis ON problem_statements(analysis_id);
CREATE INDEX idx_step1_losses_analysis ON step1_losses(analysis_id);
CREATE INDEX idx_step1_hazards_analysis ON step1_hazards(analysis_id);
CREATE INDEX idx_step1_stakeholders_analysis ON step1_stakeholders(analysis_id);
CREATE INDEX idx_adversary_profiles_analysis ON adversary_profiles(analysis_id);

CREATE INDEX idx_step1_losses_identifier ON step1_losses(analysis_id, identifier);
CREATE INDEX idx_step1_hazards_identifier ON step1_hazards(analysis_id, identifier);

CREATE INDEX idx_loss_dependencies_primary ON loss_dependencies(primary_loss_id);
CREATE INDEX idx_loss_dependencies_dependent ON loss_dependencies(dependent_loss_id);
CREATE INDEX idx_hazard_loss_mappings_hazard ON hazard_loss_mappings(hazard_id);
CREATE INDEX idx_hazard_loss_mappings_loss ON hazard_loss_mappings(loss_id);

CREATE INDEX idx_step1_stakeholders_influence ON step1_stakeholders USING GIN ((influence_interest->'influence_level'));
CREATE INDEX idx_step1_losses_severity ON step1_losses USING GIN ((severity_classification->'magnitude'));

-- =====================================================
-- VIEWS
-- =====================================================

-- Problem Framing Completeness
CREATE VIEW problem_framing_completeness AS
SELECT 
  ps.analysis_id,
  ps.full_statement,
  
  COUNT(DISTINCT l.id) as loss_count,
  COUNT(DISTINCT h.id) as hazard_count,
  COUNT(DISTINCT s.id) as stakeholder_count,
  COUNT(DISTINCT ap.id) as adversary_count,
  
  COUNT(DISTINCT hlm.loss_id) as losses_with_hazards,
  COUNT(DISTINCT l.id) - COUNT(DISTINCT hlm.loss_id) as uncovered_losses,
  
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

-- Stakeholder Loss Matrix
CREATE VIEW stakeholder_loss_matrix AS
SELECT 
  s.name as stakeholder,
  s.stakeholder_type,
  l.identifier as loss_id,
  l.description as loss_description,
  
  s.loss_exposure->'severity_perception'->>l.identifier as sensitivity_level,
  
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

-- Environmental Risk Context
CREATE VIEW environmental_risk_context AS
SELECT 
  h.identifier as hazard_id,
  h.description as hazard_description,
  
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
  
  h.temporal_nature as temporal_pattern,
  
  STRING_AGG(
    l.identifier || ' (' || 
    COALESCE(l.severity_classification->>'magnitude', 'unspecified') || ')', 
    ', '
  ) as affected_losses

FROM step1_hazards h
JOIN hazard_loss_mappings hlm ON h.id = hlm.hazard_id
JOIN step1_losses l ON hlm.loss_id = l.id
GROUP BY h.id, h.identifier, h.description, h.environmental_factors, h.temporal_nature;

-- Loss Cascade Chains
CREATE VIEW loss_cascade_chains AS
WITH RECURSIVE loss_chains AS (
    SELECT 
        id as chain_start,
        id as current_loss,
        identifier as chain_path,
        0 as depth
    FROM step1_losses
    
    UNION ALL
    
    SELECT
        lc.chain_start,
        ld.dependent_loss_id,
        lc.chain_path || ' → ' || l.identifier,
        lc.depth + 1
    FROM loss_chains lc
    JOIN loss_dependencies ld ON lc.current_loss = ld.primary_loss_id
    JOIN step1_losses l ON ld.dependent_loss_id = l.id
    WHERE lc.depth < 5
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

-- Temporal Hazard Windows
CREATE VIEW temporal_hazard_exposure AS
SELECT 
  h.identifier,
  h.description,
  h.temporal_nature->>'existence' as temporal_pattern,
  h.temporal_nature->>'when_present' as vulnerability_window,
  
  STRING_AGG(l.identifier, ', ' ORDER BY l.identifier) as exposed_losses

FROM step1_hazards h
JOIN hazard_loss_mappings hlm ON h.id = hlm.hazard_id
JOIN step1_losses l ON hlm.loss_id = l.id
WHERE h.temporal_nature->>'existence' != 'always'
  AND h.temporal_nature->>'existence' IS NOT NULL
GROUP BY h.id, h.identifier, h.description, h.temporal_nature;

-- Success State Violation Analysis
CREATE VIEW success_violation_analysis AS
SELECT 
  msc.analysis_id,
  jsonb_object_keys(msc.success_states) as success_dimension,
  msc.success_states->jsonb_object_keys(msc.success_states)->>'description' as success_description,
  msc.success_states->jsonb_object_keys(msc.success_states)->>'violated_by_losses' as violating_losses
FROM mission_success_criteria msc
WHERE msc.success_states IS NOT NULL;

-- Executive Summary
CREATE VIEW step1_executive_summary AS
SELECT
  ps.analysis_id,
  
  'This analysis examines ' || ps.purpose_what ||
  ' achieved through ' || ps.method_how ||
  ' to ' || ps.goals_why as executive_summary,
  
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
      FROM step1_losses l
      WHERE l.analysis_id = ps.analysis_id
      ORDER BY severity_order
      LIMIT 5
    ) sub
  ) as top_risks,
  
  (
    SELECT STRING_AGG(
      h.identifier || ': ' || h.description,
      E'\n'
      ORDER BY h.identifier
    )
    FROM step1_hazards h
    WHERE h.analysis_id = ps.analysis_id
      AND h.hazard_category IN ('integrity_compromised', 'mission_degraded')
  ) as critical_system_states,
  
  (SELECT COUNT(*) FROM step1_stakeholders s WHERE s.analysis_id = ps.analysis_id) as stakeholder_count,
  (SELECT COUNT(*) FROM adversary_profiles ap WHERE ap.analysis_id = ps.analysis_id) as adversary_count

FROM problem_statements ps;

-- =====================================================
-- VALIDATION FUNCTION
-- =====================================================

CREATE OR REPLACE FUNCTION validate_step1_completeness(p_analysis_id VARCHAR)
RETURNS TABLE(
  element VARCHAR,
  status VARCHAR,
  details TEXT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    'problem_statement'::VARCHAR,
    CASE WHEN COUNT(*) > 0 THEN 'complete'::VARCHAR ELSE 'missing'::VARCHAR END,
    CASE WHEN COUNT(*) > 0 THEN 'Problem statement defined'::TEXT 
         ELSE 'No problem statement found'::TEXT END
  FROM problem_statements
  WHERE analysis_id = p_analysis_id;
  
  RETURN QUERY
  SELECT 
    'losses'::VARCHAR,
    CASE WHEN COUNT(*) >= 3 THEN 'complete'::VARCHAR 
         WHEN COUNT(*) > 0 THEN 'partial'::VARCHAR 
         ELSE 'missing'::VARCHAR END,
    'Found ' || COUNT(*) || ' losses (minimum 3 recommended)'::TEXT
  FROM step1_losses
  WHERE analysis_id = p_analysis_id;
  
  RETURN QUERY
  SELECT 
    'hazards'::VARCHAR,
    CASE WHEN COUNT(*) >= 3 THEN 'complete'::VARCHAR 
         WHEN COUNT(*) > 0 THEN 'partial'::VARCHAR 
         ELSE 'missing'::VARCHAR END,
    'Found ' || COUNT(*) || ' hazards (minimum 3 recommended)'::TEXT
  FROM step1_hazards
  WHERE analysis_id = p_analysis_id;
  
  RETURN QUERY
  WITH coverage AS (
    SELECT 
      COUNT(DISTINCT l.id) as total_losses,
      COUNT(DISTINCT hlm.loss_id) as covered_losses
    FROM step1_losses l
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
  
  RETURN QUERY
  SELECT 
    'stakeholders'::VARCHAR,
    CASE WHEN COUNT(*) >= 3 THEN 'complete'::VARCHAR 
         WHEN COUNT(*) > 0 THEN 'partial'::VARCHAR 
         ELSE 'missing'::VARCHAR END,
    'Found ' || COUNT(*) || ' stakeholders'::TEXT
  FROM step1_stakeholders
  WHERE analysis_id = p_analysis_id;
  
  RETURN QUERY
  SELECT 
    'adversaries'::VARCHAR,
    CASE WHEN COUNT(*) >= 1 THEN 'complete'::VARCHAR 
         ELSE 'missing'::VARCHAR END,
    'Found ' || COUNT(*) || ' adversary profiles'::TEXT
  FROM adversary_profiles
  WHERE analysis_id = p_analysis_id;
  
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

COMMENT ON SCHEMA public IS 'STPA-Sec Step 1 Schema v1.0 - Clean version with prefixed tables';