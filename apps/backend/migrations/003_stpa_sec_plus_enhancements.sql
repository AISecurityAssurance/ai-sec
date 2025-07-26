-- STPA-Sec+ Enhancement Tables Migration
-- Phase 1: Core Implementation (Weeks 1-2) - Part 3
-- This migration adds STPA-Sec+ specific enhancements including privacy, data flows, and advanced analysis

-- Privacy Analysis Integration (LINDDUN)
CREATE TABLE privacy_threats (
  id VARCHAR PRIMARY KEY,
  relationship_id VARCHAR REFERENCES relationships(id),
  data_flow_id VARCHAR, -- Will reference data_flows table
  
  -- LINDDUN Categories
  linking JSONB,
  /* Example:
  {
    "exists": true,
    "description": "User sessions can be linked across services",
    "data_elements": ["session_id", "device_fingerprint"],
    "severity": "high",
    "gdpr_violation": true
  }
  */
  identifying JSONB,
  non_repudiation JSONB,
  detecting JSONB,
  data_disclosure JSONB,
  unawareness JSONB,
  non_compliance JSONB,
  
  -- Privacy Impact Assessment
  privacy_impact JSONB,
  /* Example:
  {
    "affected_data_subjects": ["customers", "employees"],
    "data_categories": ["financial", "behavioral", "biometric"],
    "retention_violation": true,
    "cross_border_transfer": true,
    "consent_issues": ["unclear_purpose", "no_opt_out"]
  }
  */
  
  regulatory_context JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Data flow mapping for privacy analysis
CREATE TABLE data_flows (
  id VARCHAR PRIMARY KEY,
  source_entity VARCHAR REFERENCES entities(id),
  target_entity VARCHAR REFERENCES entities(id),
  
  data_classification JSONB,
  /* Example:
  {
    "categories": ["pii", "financial", "health"],
    "sensitivity": "high",
    "regulatory_scope": ["gdpr", "ccpa", "hipaa"]
  }
  */
  
  flow_properties JSONB,
  /* Example:
  {
    "encryption_in_transit": "tls_1.3",
    "encryption_at_rest": "aes_256",
    "anonymization": "k_anonymity_5",
    "retention_period": "90_days",
    "deletion_capability": "automated"
  }
  */
  
  purpose_limitation JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Add foreign key constraint for privacy_threats
ALTER TABLE privacy_threats 
  ADD CONSTRAINT fk_privacy_threats_data_flow 
  FOREIGN KEY (data_flow_id) REFERENCES data_flows(id);

-- PASTA Stage Tracking
CREATE TABLE pasta_analysis_stages (
  id VARCHAR PRIMARY KEY,
  analysis_id VARCHAR,
  
  -- 7 PASTA Stages
  stage1_business_objectives JSONB,
  stage2_technical_scope JSONB,
  stage3_application_decomposition JSONB,
  stage4_threat_analysis JSONB,
  stage5_vulnerability_analysis JSONB,
  stage6_attack_modeling JSONB,
  stage7_risk_management JSONB,
  
  -- Evidence collection
  evidence_sources JSONB,
  /* Example:
  {
    "threat_intel_feeds": ["misp", "taxii", "vendor_reports"],
    "vulnerability_scans": ["nessus", "qualys", "custom"],
    "business_impact_analysis": "bia_2024_q1.pdf",
    "penetration_tests": ["external_2024", "internal_2023"]
  }
  */
  
  completion_status JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Wargaming Sessions
CREATE TABLE wargaming_sessions (
  id VARCHAR PRIMARY KEY,
  scenario_id VARCHAR REFERENCES scenarios(id),
  session_date TIMESTAMP DEFAULT NOW(),
  participants JSONB,
  
  -- Red team analysis
  red_team_moves JSONB,
  /* Example:
  {
    "move_sequence": [
      {
        "move": 1,
        "action": "Reconnaissance",
        "target": "Authentication Service",
        "method": "Port scanning and service enumeration",
        "expected_outcome": "Identify service versions",
        "blue_visibility": "low"
      },
      {
        "move": 2,
        "action": "Initial compromise",
        "target": "Web application",
        "method": "SQL injection in search function",
        "expected_outcome": "Database access",
        "blue_visibility": "medium"
      }
    ],
    "total_moves": 5,
    "estimated_time": "3 days"
  }
  */
  
  -- Blue team responses
  blue_team_responses JSONB,
  /* Example:
  {
    "detections": [
      {
        "move_detected": 2,
        "detection_method": "WAF alert",
        "response_time": "15 minutes",
        "action_taken": "Block IP, investigate logs"
      }
    ],
    "missed_detections": [1],
    "response_effectiveness": "partial"
  }
  */
  
  -- Purple team synthesis
  effectiveness_assessment JSONB,
  /* Example:
  {
    "detection_rate": "60%",
    "response_time_avg": "25 minutes",
    "containment_success": "partial",
    "gaps_identified": [
      "Reconnaissance detection",
      "Lateral movement visibility"
    ],
    "control_effectiveness": {
      "preventive": "40%",
      "detective": "60%",
      "corrective": "70%"
    }
  }
  */
  
  lessons_learned TEXT[],
  recommended_improvements TEXT[],
  
  properties JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Link wargaming results back to mitigations
CREATE TABLE wargaming_mitigation_updates (
  session_id VARCHAR REFERENCES wargaming_sessions(id),
  mitigation_id VARCHAR REFERENCES mitigations(id),
  effectiveness_update VARCHAR, -- New effectiveness based on wargaming
  implementation_changes TEXT[],
  priority_change INT, -- Delta to priority
  
  PRIMARY KEY (session_id, mitigation_id)
);

-- Threat Intelligence Integration
CREATE TABLE threat_landscape_intelligence (
  id VARCHAR PRIMARY KEY,
  threat_category VARCHAR CHECK (threat_category IN ('traditional', 'ai_ml', 'privacy', 'supply_chain', 'insider', 'nation_state')),
  threat_name VARCHAR NOT NULL,
  emergence_date DATE,
  
  -- Industry relevance
  industry_relevance JSONB,
  /* Example:
  {
    "financial_services": {"relevance": "critical", "specific_risks": ["payment_fraud", "account_takeover"]},
    "healthcare": {"relevance": "high", "specific_risks": ["data_exfiltration", "ransomware"]},
    "government": {"relevance": "critical", "specific_risks": ["espionage", "service_disruption"]}
  }
  */
  
  -- Framework implications
  stpa_sec_plus_implications JSONB,
  /* Example:
  {
    "new_attack_vectors": ["llm_manipulation", "training_data_poisoning"],
    "affected_components": ["ai_agents", "decision_systems"],
    "recommended_analyses": ["maestro_layer_assessment", "adversarial_testing"],
    "mitigation_strategies": ["input_validation", "model_monitoring"]
  }
  */
  
  -- Threat evolution tracking
  evolution_history JSONB,
  current_variants TEXT[],
  predicted_evolution TEXT[],
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Automated threat feed integration
CREATE TABLE automated_threat_feeds (
  id VARCHAR PRIMARY KEY,
  feed_source VARCHAR NOT NULL,  -- 'mitre_attack', 'cisa_alerts', 'vendor_intelligence'
  feed_type VARCHAR CHECK (feed_type IN ('ioc', 'ttp', 'vulnerability', 'campaign', 'ai_specific')),
  
  last_update TIMESTAMP,
  update_frequency VARCHAR,  -- 'real_time', 'hourly', 'daily'
  
  -- Threat data
  relevant_threats JSONB,
  /* Example:
  {
    "new_threats": [
      {
        "id": "T2024.001",
        "name": "LLM Prompt Injection Campaign",
        "severity": "high",
        "targets": ["customer_service_bots", "code_assistants"]
      }
    ],
    "updated_threats": [...],
    "deprecated_threats": [...]
  }
  */
  
  -- Automatic mapping to STPA-Sec+
  stpa_sec_plus_mappings JSONB,
  /* Example:
  {
    "mapped_entities": ["E-001", "E-015"],
    "suggested_analyses": ["hazop_ai_deviation", "linddun_llm_privacy"],
    "priority_level": "immediate"
  }
  */
  
  integration_status VARCHAR CHECK (integration_status IN ('active', 'paused', 'error')),
  created_at TIMESTAMP DEFAULT NOW()
);

-- Link threats to affected analyses
CREATE TABLE threat_analysis_mappings (
  threat_id VARCHAR REFERENCES threat_landscape_intelligence(id),
  analysis_id VARCHAR REFERENCES analyses(id),
  relevance_score FLOAT CHECK (relevance_score >= 0 AND relevance_score <= 1),
  mapping_rationale TEXT,
  requires_reanalysis BOOLEAN DEFAULT FALSE,
  PRIMARY KEY (threat_id, analysis_id)
);

-- Compliance Requirements Tracking
CREATE TABLE compliance_requirements (
  id VARCHAR PRIMARY KEY,
  regulation_name VARCHAR NOT NULL,  -- 'GDPR', 'CCPA', 'HIPAA', 'PCI-DSS', 'SOC2'
  
  -- Required controls mapping
  required_controls JSONB,
  /* Example:
  {
    "data_protection": ["encryption_at_rest", "encryption_in_transit"],
    "access_control": ["mfa", "rbac", "audit_logging"],
    "privacy_rights": ["data_portability", "right_to_deletion"],
    "incident_response": ["breach_notification_72h", "impact_assessment"]
  }
  */
  
  -- Penalty structure
  penalty_structure JSONB,
  /* Example:
  {
    "max_fine": {"amount": 20000000, "currency": "EUR", "basis": "4%_global_revenue"},
    "typical_fine": {"amount": 5000000, "currency": "EUR"},
    "enforcement_trend": "increasing"
  }
  */
  
  jurisdiction TEXT[],
  effective_date DATE,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Map mitigations to compliance
CREATE TABLE privacy_compliance (
  regulation VARCHAR,
  required_mitigations VARCHAR[],
  implemented_mitigations VARCHAR[],
  gap_analysis JSONB,
  last_audit DATE,
  PRIMARY KEY (regulation)
);

-- Helper table for implemented controls
CREATE TABLE implemented_mitigations (
  id VARCHAR PRIMARY KEY,
  mitigation_id VARCHAR REFERENCES mitigations(id),
  control_type VARCHAR NOT NULL,
  implementation_date DATE,
  last_tested DATE,
  test_results JSONB,
  audit_evidence JSONB,  -- Links to documents, logs, etc.
  created_at TIMESTAMP DEFAULT NOW()
);

-- Mission criticality tracking
CREATE TABLE mission_criticality (
  id VARCHAR PRIMARY KEY,
  mission_element VARCHAR NOT NULL,
  scenario_id VARCHAR REFERENCES scenarios(id),
  current_risk FLOAT,
  residual_risk FLOAT,
  risk_value_reduction NUMERIC,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Cross-framework validation function
CREATE OR REPLACE FUNCTION validate_cross_framework_consistency() RETURNS TABLE(
  issue_type VARCHAR,
  entity_id VARCHAR,
  description TEXT,
  severity VARCHAR
) AS $$
BEGIN
  RETURN QUERY
  
  -- Check for STRIDE without corresponding HAZOP analysis
  SELECT 
    'missing_hazop_analysis' as issue_type,
    r.id as entity_id,
    'STRIDE analysis exists without HAZOP deviation analysis' as description,
    'medium' as severity
  FROM relationships r
  JOIN analyses a ON r.id = a.relationship_id
  WHERE a.stride_spoofing IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM hazop_deviations h WHERE h.relationship_id = r.id)
  
  UNION ALL
  
  -- Check for AI entities without MAESTRO layer analysis
  SELECT 
    'missing_ai_layer_analysis' as issue_type,
    e.id as entity_id,
    'AI entity without layer vulnerability analysis' as description,
    'high' as severity
  FROM entities e
  WHERE e.ai_properties IS NOT NULL
    AND NOT EXISTS (SELECT 1 FROM ai_agent_layers aal WHERE aal.agent_id = e.id)
  
  UNION ALL
  
  -- Check for privacy data flows without LINDDUN analysis
  SELECT 
    'missing_privacy_analysis' as issue_type,
    df.id as entity_id,
    'Sensitive data flow without privacy threat analysis' as description,
    'high' as severity
  FROM data_flows df
  WHERE df.data_classification->>'sensitivity' = 'high'
    AND NOT EXISTS (SELECT 1 FROM privacy_threats pt WHERE pt.data_flow_id = df.id);
    
END;
$$ LANGUAGE plpgsql;