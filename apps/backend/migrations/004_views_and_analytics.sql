-- STPA-Sec+ Views and Analytics Migration
-- Phase 1: Core Implementation (Weeks 1-2) - Part 4
-- This migration creates analytical views and helper functions

-- Traceability Views

-- Complete traceability from mitigation to stakeholder
CREATE VIEW mitigation_impact_analysis AS
WITH RECURSIVE impact_chain AS (
  SELECT 
    m.id as mitigation_id,
    m.name as mitigation_name,
    s.id as scenario_id,
    s.hazard_refs,
    s.risk_score as scenario_risk
  FROM mitigations m
  JOIN scenario_mitigations sm ON m.id = sm.mitigation_id
  JOIN scenarios s ON sm.scenario_id = s.id
)
SELECT 
  ic.mitigation_id,
  ic.mitigation_name,
  COUNT(DISTINCT ic.scenario_id) as scenarios_addressed,
  COUNT(DISTINCT h.id) as hazards_mitigated,
  COUNT(DISTINCT l.id) as losses_prevented,
  COUNT(DISTINCT sh.id) as stakeholders_protected,
  SUM(ic.scenario_risk) as total_risk_reduction,
  array_agg(DISTINCT sh.name) as affected_stakeholders
FROM impact_chain ic
JOIN hazards h ON h.id = ANY(ic.hazard_refs)
JOIN losses l ON l.id = ANY(h.loss_refs)
JOIN stakeholders sh ON sh.id = ANY(l.stakeholder_refs)
GROUP BY ic.mitigation_id, ic.mitigation_name
ORDER BY total_risk_reduction DESC;

-- Entity relationship complexity
CREATE VIEW entity_complexity AS
SELECT 
  e.id,
  e.name,
  COUNT(DISTINCT r1.id) as outgoing_controls,
  COUNT(DISTINCT r2.id) as incoming_controls,
  COUNT(DISTINCT r3.id) as outgoing_feedback,
  COUNT(DISTINCT r4.id) as incoming_feedback,
  COUNT(DISTINCT r1.id) + COUNT(DISTINCT r2.id) + 
  COUNT(DISTINCT r3.id) + COUNT(DISTINCT r4.id) as total_relationships
FROM entities e
LEFT JOIN relationships r1 ON e.id = r1.source_id AND r1.type = 'control'
LEFT JOIN relationships r2 ON e.id = r2.target_id AND r2.type = 'control'
LEFT JOIN relationships r3 ON e.id = r3.source_id AND r3.type = 'feedback'
LEFT JOIN relationships r4 ON e.id = r4.target_id AND r4.type = 'feedback'
GROUP BY e.id, e.name
ORDER BY total_relationships DESC;

-- Mission Impact Traceability
CREATE VIEW mission_impact_traceability AS
SELECT 
  m.id as mitigation_id,
  m.name as mitigation_name,
  
  -- Mission impact metrics
  COUNT(DISTINCT sd.mission_criticality->>'primary_mission') as missions_protected,
  
  -- Risk reduction in mission terms
  JSON_AGG(DISTINCT 
    JSON_BUILD_OBJECT(
      'mission_element', mc.mission_element,
      'current_risk', mc.current_risk,
      'residual_risk', mc.residual_risk,
      'risk_reduction', mc.current_risk - mc.residual_risk
    )
  ) as mission_risk_reduction,
  
  -- Cost-benefit in mission context
  CASE 
    WHEN m.cost_estimate->>'initial' IS NOT NULL 
    THEN (SUM(mc.risk_value_reduction) / (m.cost_estimate->'initial'->>'amount')::FLOAT)
    ELSE NULL 
  END as roi_score

FROM mitigations m
JOIN scenario_mitigations sm ON m.id = sm.mitigation_id
JOIN scenarios s ON sm.scenario_id = s.id
JOIN mission_criticality mc ON mc.scenario_id = s.id
JOIN system_definition sd ON sd.id = 'system-001'
GROUP BY m.id, m.name, m.cost_estimate;

-- Adversarial Analysis View
CREATE VIEW adversary_capability_coverage AS
SELECT 
  a.name as adversary,
  a.type as adversary_type,
  
  -- Attack surface analysis
  COUNT(DISTINCT acp.entity_id) as controlled_entities,
  COUNT(DISTINCT r.id) as influenced_relationships,
  
  -- Defensive coverage
  COUNT(DISTINCT m.id) as applicable_mitigations,
  AVG(CASE 
    WHEN m.effectiveness = 'low' THEN 1
    WHEN m.effectiveness = 'medium' THEN 2
    WHEN m.effectiveness = 'high' THEN 3
    WHEN m.effectiveness = 'very_high' THEN 4
    ELSE 0
  END) as avg_mitigation_effectiveness,
  
  -- Gaps
  ARRAY_AGG(DISTINCT 
    CASE 
      WHEN m.id IS NULL THEN acp.entity_id 
      ELSE NULL 
    END
  ) FILTER (WHERE m.id IS NULL) as unmitigated_control_points

FROM adversaries a
JOIN adversary_control_problems acp ON a.id = acp.adversary_id
LEFT JOIN relationships r ON r.source_id = acp.entity_id OR r.target_id = acp.entity_id
LEFT JOIN analyses an ON an.relationship_id = r.id
LEFT JOIN scenarios s ON s.relationship_id = r.id 
  AND a.id = ANY(s.threat_actor_refs)
LEFT JOIN scenario_mitigations sm ON sm.scenario_id = s.id
LEFT JOIN mitigations m ON m.id = sm.mitigation_id

GROUP BY a.id, a.name, a.type;

-- Temporal Risk View
CREATE VIEW temporal_risk_windows AS
SELECT 
  tc.time_window,
  tc.window_type,
  COUNT(DISTINCT a.id) as active_vulnerabilities,
  MAX(s.risk_score) as peak_risk,
  ARRAY_AGG(DISTINCT s.description) as critical_scenarios

FROM (
  SELECT DISTINCT 
    jsonb_array_elements_text(temporal_context->'timing_windows'->'critical') as time_window,
    'critical' as window_type
  FROM analyses
  WHERE temporal_context IS NOT NULL
) tc
JOIN analyses a ON a.temporal_context->'timing_windows'->'critical' ? tc.time_window
JOIN scenarios s ON s.uca_refs && ARRAY[a.id]
GROUP BY tc.time_window, tc.window_type
ORDER BY peak_risk DESC;

-- D4 Analysis View
CREATE VIEW d4_priority_analysis AS
SELECT 
  s.id as scenario_id,
  s.description,
  r.source_id || ' -> ' || r.target_id || ': ' || r.action as relationship,
  
  -- Individual D4 scores
  (s.d4_assessment->>'detectability')::INT as detectability,
  (s.d4_assessment->>'difficulty')::INT as difficulty,
  (s.d4_assessment->>'damage')::INT as damage,
  (s.d4_assessment->>'deniability')::INT as deniability,
  (s.d4_assessment->>'overall_score')::INT as d4_total,
  
  -- Risk context
  s.risk_score,
  s.likelihood,
  s.impact,
  
  -- Mitigation status
  COUNT(DISTINCT sm.mitigation_id) as mitigation_count,
  STRING_AGG(DISTINCT sm.effectiveness_for_scenario, ', ') as mitigation_effectiveness,
  
  -- Priority recommendation
  CASE 
    WHEN (s.d4_assessment->>'overall_score')::INT >= 16 AND s.risk_score >= 16 THEN 'CRITICAL'
    WHEN (s.d4_assessment->>'overall_score')::INT >= 12 OR s.risk_score >= 12 THEN 'HIGH'
    WHEN (s.d4_assessment->>'overall_score')::INT >= 8 OR s.risk_score >= 8 THEN 'MEDIUM'
    ELSE 'LOW'
  END as priority_recommendation

FROM scenarios s
JOIN relationships r ON s.relationship_id = r.id
LEFT JOIN scenario_mitigations sm ON s.id = sm.scenario_id
WHERE s.d4_assessment IS NOT NULL
GROUP BY s.id, s.description, s.d4_assessment, s.risk_score, s.likelihood, s.impact, r.source_id, r.target_id, r.action
ORDER BY d4_total DESC, s.risk_score DESC;

-- Comprehensive Security Posture
CREATE VIEW comprehensive_security_posture AS
WITH risk_aggregation AS (
  SELECT 
    e.id as entity_id,
    e.name as entity_name,
    
    -- Traditional security risks
    COUNT(DISTINCT a.id) FILTER (WHERE a.analysis_type = 'stpa-sec') as stpa_risks,
    COUNT(DISTINCT a.id) FILTER (WHERE a.analysis_type = 'stride') as stride_risks,
    
    -- AI-specific risks
    COUNT(DISTINCT aal.vulnerabilities) as ai_vulnerabilities,
    
    -- Privacy risks
    COUNT(DISTINCT pt.id) as privacy_threats,
    
    -- Quantitative metrics
    AVG(urs.normalized_score) as avg_risk_score,
    MAX(urs.business_impact_dollars) as max_business_impact
    
  FROM entities e
  LEFT JOIN relationships r ON e.id IN (r.source_id, r.target_id)
  LEFT JOIN analyses a ON r.id = a.relationship_id
  LEFT JOIN ai_agent_layers aal ON e.id = aal.agent_id
  LEFT JOIN privacy_threats pt ON r.id = pt.relationship_id
  LEFT JOIN scenarios s ON r.id = s.relationship_id
  LEFT JOIN unified_risk_scores urs ON s.id = urs.scenario_id
  GROUP BY e.id, e.name
)
SELECT 
  entity_id,
  entity_name,
  stpa_risks + stride_risks + ai_vulnerabilities + privacy_threats as total_risks,
  
  -- Risk breakdown
  JSON_BUILD_OBJECT(
    'security', stpa_risks + stride_risks,
    'ai_specific', ai_vulnerabilities,
    'privacy', privacy_threats
  ) as risk_distribution,
  
  -- Business context
  avg_risk_score,
  max_business_impact,
  
  -- Coverage assessment
  CASE 
    WHEN stpa_risks > 0 AND ai_vulnerabilities > 0 AND privacy_threats > 0 THEN 'comprehensive'
    WHEN stpa_risks > 0 AND (ai_vulnerabilities > 0 OR privacy_threats > 0) THEN 'good'
    WHEN stpa_risks > 0 THEN 'basic'
    ELSE 'insufficient'
  END as coverage_level

FROM risk_aggregation
ORDER BY total_risks DESC, max_business_impact DESC;

-- AI Agent Risk Assessment
CREATE VIEW ai_agent_risk_assessment AS
SELECT 
  e.id,
  e.name,
  e.ai_properties->>'ai_type' as ai_type,
  e.ai_properties->>'autonomy_level' as autonomy_level,
  
  -- Layer-specific vulnerabilities
  JSON_AGG(
    JSON_BUILD_OBJECT(
      'layer', aal.layer_type,
      'vulnerabilities', aal.vulnerabilities,
      'controls', aal.security_controls
    )
  ) as layer_analysis,
  
  -- Unique AI risks
  COUNT(DISTINCT aal.vulnerabilities->>'prompt_injection') as prompt_injection_risks,
  COUNT(DISTINCT aal.vulnerabilities->>'hallucination') as hallucination_risks,
  COUNT(DISTINCT aal.vulnerabilities->>'data_poisoning') as data_poisoning_risks,
  
  -- Mitigation coverage
  COUNT(DISTINCT aal.security_controls) as implemented_controls,
  
  -- Risk priority
  CASE 
    WHEN e.ai_properties->>'autonomy_level' = 'autonomous' 
      AND COUNT(DISTINCT aal.vulnerabilities) > 5 THEN 'CRITICAL'
    WHEN COUNT(DISTINCT aal.vulnerabilities) > 3 THEN 'HIGH'
    WHEN COUNT(DISTINCT aal.vulnerabilities) > 0 THEN 'MEDIUM'
    ELSE 'LOW'
  END as ai_risk_priority

FROM entities e
JOIN ai_agent_layers aal ON e.id = aal.agent_id
WHERE e.ai_properties IS NOT NULL
GROUP BY e.id, e.name, e.ai_properties
ORDER BY ai_risk_priority DESC;

-- Security Investment Optimization
CREATE VIEW security_investment_optimization AS
WITH investment_analysis AS (
  SELECT 
    m.id as mitigation_id,
    m.name as mitigation_name,
    m.type as mitigation_type,
    
    -- Cost analysis
    (m.cost_estimate->>'initial')::NUMERIC as initial_cost,
    (m.cost_estimate->'recurring'->>'amount')::NUMERIC as recurring_cost,
    
    -- Risk reduction calculation
    COUNT(DISTINCT s.id) as scenarios_mitigated,
    SUM(s.risk_score) as total_risk_reduced,
    SUM(urs.business_impact_dollars) as potential_loss_prevented,
    
    -- Implementation factors
    m.implementation_difficulty,
    COALESCE(m.implementation_steps, ARRAY[]::TEXT[]) as steps_required,
    
    -- Compliance benefits
    COUNT(DISTINCT pc.regulation) as regulations_addressed
    
  FROM mitigations m
  JOIN scenario_mitigations sm ON m.id = sm.mitigation_id
  JOIN scenarios s ON sm.scenario_id = s.id
  LEFT JOIN unified_risk_scores urs ON s.id = urs.scenario_id
  LEFT JOIN privacy_compliance pc ON m.id = ANY(pc.required_mitigations)
  GROUP BY m.id, m.name, m.type, m.cost_estimate, m.implementation_difficulty
)
SELECT 
  mitigation_id,
  mitigation_name,
  initial_cost,
  recurring_cost,
  total_risk_reduced,
  potential_loss_prevented,
  
  -- ROI Calculation
  CASE 
    WHEN initial_cost > 0 THEN 
      ((potential_loss_prevented - initial_cost - (recurring_cost * 3)) / initial_cost * 100)::INT
    ELSE NULL 
  END as roi_percentage,
  
  -- Implementation complexity score
  CASE implementation_difficulty
    WHEN 'trivial' THEN 1
    WHEN 'easy' THEN 2
    WHEN 'moderate' THEN 3
    WHEN 'hard' THEN 4
    WHEN 'extreme' THEN 5
  END as complexity_score,
  
  -- Strategic value
  regulations_addressed * 100000 as regulatory_value,  -- Rough GDPR fine avoidance
  
  -- Priority recommendation
  CASE 
    WHEN ((potential_loss_prevented - initial_cost - (recurring_cost * 3)) / NULLIF(initial_cost, 0) * 100) > 300 
      AND CASE implementation_difficulty
        WHEN 'trivial' THEN 1
        WHEN 'easy' THEN 2
        WHEN 'moderate' THEN 3
        WHEN 'hard' THEN 4
        WHEN 'extreme' THEN 5
      END <= 3 THEN 'immediate'
    WHEN ((potential_loss_prevented - initial_cost - (recurring_cost * 3)) / NULLIF(initial_cost, 0) * 100) > 200 
      OR regulations_addressed > 2 THEN 'high'
    WHEN ((potential_loss_prevented - initial_cost - (recurring_cost * 3)) / NULLIF(initial_cost, 0) * 100) > 100 THEN 'medium'
    ELSE 'low'
  END as implementation_priority

FROM investment_analysis
ORDER BY roi_percentage DESC NULLS LAST, total_risk_reduced DESC;

-- Regulatory Compliance Status
CREATE VIEW regulatory_compliance_status AS
SELECT 
  cr.regulation_name,
  cr.jurisdiction,
  
  -- Control coverage
  JSON_BUILD_OBJECT(
    'required', CARDINALITY(ARRAY(SELECT DISTINCT jsonb_array_elements_text(cr.required_controls->'data_protection'))),
    'implemented', COUNT(DISTINCT im.control_type),
    'coverage_percentage', 
      CASE 
        WHEN CARDINALITY(ARRAY(SELECT DISTINCT jsonb_array_elements_text(cr.required_controls->'data_protection'))) > 0
        THEN (COUNT(DISTINCT im.control_type)::FLOAT / 
              CARDINALITY(ARRAY(SELECT DISTINCT jsonb_array_elements_text(cr.required_controls->'data_protection')))::FLOAT * 100)::INT
        ELSE 100
      END
  ) as control_coverage,
  
  -- Risk exposure
  (cr.penalty_structure->'max_fine'->>'amount')::NUMERIC as max_penalty,
  
  -- Audit readiness
  CASE 
    WHEN COUNT(DISTINCT im.control_type)::FLOAT / 
         NULLIF(CARDINALITY(ARRAY(SELECT DISTINCT jsonb_array_elements_text(cr.required_controls->'data_protection'))), 0)::FLOAT >= 0.95 
    THEN 'audit_ready'
    WHEN COUNT(DISTINCT im.control_type)::FLOAT / 
         NULLIF(CARDINALITY(ARRAY(SELECT DISTINCT jsonb_array_elements_text(cr.required_controls->'data_protection'))), 0)::FLOAT >= 0.80 
    THEN 'nearly_ready'
    ELSE 'gaps_exist'
  END as audit_status,
  
  -- Evidence collection
  JSON_AGG(DISTINCT 
    JSON_BUILD_OBJECT(
      'control', im.control_type,
      'evidence', im.audit_evidence,
      'last_tested', im.last_tested
    )
  ) as audit_evidence

FROM compliance_requirements cr
LEFT JOIN implemented_mitigations im ON im.control_type = ANY(ARRAY(SELECT jsonb_array_elements_text(cr.required_controls->'data_protection')))
GROUP BY cr.regulation_name, cr.jurisdiction, cr.required_controls, cr.penalty_structure
ORDER BY max_penalty DESC;

-- Data Validation Functions

-- Ensure all UCAs link to valid hazards
CREATE OR REPLACE FUNCTION validate_uca_hazard_links() RETURNS BOOLEAN AS $$
DECLARE
  invalid_count INT;
BEGIN
  SELECT COUNT(*) INTO invalid_count
  FROM analyses a
  WHERE 
    (a.uca_not_provided->>'exists' = 'true' AND 
     NOT (a.uca_not_provided->'hazard_refs' ?| array(SELECT id FROM hazards)))
    OR
    (a.uca_provided_causes_hazard->>'exists' = 'true' AND 
     NOT (a.uca_provided_causes_hazard->'hazard_refs' ?| array(SELECT id FROM hazards)))
    OR
    (a.uca_wrong_timing->>'exists' = 'true' AND 
     NOT (a.uca_wrong_timing->'hazard_refs' ?| array(SELECT id FROM hazards)))
    OR
    (a.uca_stopped_too_soon->>'exists' = 'true' AND 
     NOT (a.uca_stopped_too_soon->'hazard_refs' ?| array(SELECT id FROM hazards)));
    
  RETURN invalid_count = 0;
END;
$$ LANGUAGE plpgsql;

-- Check for orphaned relationships
CREATE OR REPLACE FUNCTION find_incomplete_analyses() RETURNS TABLE(
  relationship_id VARCHAR,
  missing_analyses TEXT[]
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    r.id,
    array_agg(
      CASE 
        WHEN a.id IS NULL THEN 'No analysis'
        WHEN a.uca_not_provided IS NULL THEN 'Missing UCA analysis'
        WHEN a.stride_spoofing IS NULL THEN 'Missing STRIDE analysis'
      END
    )
  FROM relationships r
  LEFT JOIN analyses a ON r.id = a.relationship_id
  WHERE a.id IS NULL 
     OR a.uca_not_provided IS NULL 
     OR a.stride_spoofing IS NULL
  GROUP BY r.id;
END;
$$ LANGUAGE plpgsql;

-- Critical unmitigated scenarios
CREATE VIEW critical_unmitigated_scenarios AS
SELECT 
  s.id,
  s.description,
  s.risk_score,
  r.source_id || ' -> ' || r.target_id as relationship,
  r.action,
  array_length(s.hazard_refs, 1) as hazard_count
FROM scenarios s
JOIN relationships r ON s.relationship_id = r.id
LEFT JOIN scenario_mitigations sm ON s.id = sm.scenario_id
WHERE sm.scenario_id IS NULL
  AND s.risk_score >= 15  -- High risk (3x5 or higher)
ORDER BY s.risk_score DESC;

-- Entity exposure analysis
CREATE VIEW entity_exposure_analysis AS
SELECT 
  e.name,
  e.trust_level,
  e.exposure,
  COUNT(DISTINCT a.id) as total_vulnerabilities,
  COUNT(DISTINCT CASE WHEN a.uca_not_provided->>'severity' = 'critical' THEN a.id END) as critical_ucas,
  COUNT(DISTINCT CASE WHEN a.stride_spoofing->>'severity' = 'critical' THEN a.id END) as critical_stride
FROM entities e
JOIN relationships r ON e.id IN (r.source_id, r.target_id)
JOIN analyses a ON r.id = a.relationship_id
WHERE e.exposure = 'external'
GROUP BY e.id, e.name, e.trust_level, e.exposure
ORDER BY critical_ucas DESC, critical_stride DESC;