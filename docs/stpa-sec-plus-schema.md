# STPA-Sec+ Enhanced Schema

## Overview
STPA-Sec+ extends the core STPA-Sec methodology to address critical gaps in AI/ML security, privacy protection, quantitative risk assessment, and systematic deviation analysis. This schema builds upon our enhanced STPA-Sec foundation while integrating the unique strengths of MAESTRO, PASTA, HAZOP, LINDDUN, and DREAD frameworks.

## Core Philosophy
- **Mission-First**: Maintain STPA-Sec's focus on mission impact
- **AI-Native**: Built for systems where AI/ML is pervasive
- **Privacy-Aware**: Privacy as a first-class security concern
- **Quantitative**: Multiple scoring methodologies for executive decisions
- **Systematic**: Comprehensive coverage through multiple lenses

## Enhanced Entities for AI/ML Systems (MAESTRO Integration)

### AI-Enhanced Entities
```sql
-- Extend the base entities table for AI/ML components
ALTER TABLE entities ADD COLUMN ai_properties JSONB;
/* Example:
{
  "ai_type": "llm",  -- llm, ml_model, agent, ensemble
  "model_details": {
    "architecture": "transformer",
    "parameters": "70B",
    "training_data": "public_internet",
    "fine_tuning": "custom_banking_data"
  },
  "capabilities": {
    "reasoning": true,
    "tool_use": true,
    "memory": "context_window",
    "learning": "in_context"
  },
  "autonomy_level": "supervised",  -- none, supervised, autonomous
  "decision_authority": ["recommendations", "data_access"],
  "trust_boundaries": {
    "input_validation": "required",
    "output_verification": "human_review"
  }
}
*/

-- MAESTRO Agent Layers
CREATE TABLE ai_agent_layers (
  agent_id VARCHAR REFERENCES entities(id),
  layer_type VARCHAR CHECK (layer_type IN ('perception', 'reasoning', 'planning', 'execution', 'learning')),
  
  -- Layer-specific vulnerabilities
  vulnerabilities JSONB,
  /* Example:
  {
    "perception": {
      "prompt_injection": {"severity": "high", "mitigations": ["input_sanitization"]},
      "adversarial_inputs": {"severity": "critical", "mitigations": ["robust_training"]}
    },
    "reasoning": {
      "hallucination": {"severity": "medium", "frequency": "occasional"},
      "bias_amplification": {"severity": "high", "source": "training_data"}
    }
  }
  */
  
  -- Inter-layer dependencies
  dependencies JSONB,
  security_controls JSONB,
  
  PRIMARY KEY (agent_id, layer_type)
);
```

## Privacy Analysis Integration (LINDDUN)

### Privacy-Specific Threat Modeling
```sql
CREATE TABLE privacy_threats (
  id VARCHAR PRIMARY KEY,
  relationship_id VARCHAR REFERENCES relationships(id),
  data_flow_id VARCHAR REFERENCES data_flows(id),
  
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
```

## Quantitative Risk Assessment (DREAD Integration)

### DREAD Scoring for All Threats
```sql
-- Extend analyses table with DREAD scoring
ALTER TABLE analyses ADD COLUMN dread_assessment JSONB;
/* Example:
{
  "damage_potential": {
    "score": 8,
    "rationale": "Complete system compromise possible",
    "impact_areas": ["data_breach", "service_outage", "reputation"]
  },
  "reproducibility": {
    "score": 6,
    "rationale": "Requires specific conditions but scriptable"
  },
  "exploitability": {
    "score": 7,
    "rationale": "Moderate skill required, tools available"
  },
  "affected_users": {
    "score": 9,
    "rationale": "All users potentially affected",
    "user_count": "1M+",
    "user_categories": ["retail", "business", "admin"]
  },
  "discoverability": {
    "score": 4,
    "rationale": "Not obvious but findable through testing"
  },
  "total_score": 34,
  "risk_level": "CRITICAL"  -- Based on score thresholds
}
*/

-- Comparative risk scoring across frameworks
CREATE TABLE unified_risk_scores (
  scenario_id VARCHAR REFERENCES scenarios(id),
  
  -- Multiple scoring methodologies
  stpa_risk_score FLOAT,      -- Impact × Likelihood
  dread_score INT,            -- Sum of DREAD components
  cvss_score FLOAT,           -- If applicable
  fair_score JSONB,           -- Factor Analysis of Information Risk
  
  -- Normalized scores for comparison
  normalized_score FLOAT,      -- 0-100 scale
  confidence_level VARCHAR,    -- low, medium, high
  
  -- Executive metrics
  business_impact_dollars NUMERIC,
  mitigation_roi FLOAT,
  
  PRIMARY KEY (scenario_id)
);
```

## Systematic Deviation Analysis (HAZOP Integration)

### Guide Word Analysis for Control Actions
```sql
CREATE TABLE hazop_deviations (
  id VARCHAR PRIMARY KEY,
  relationship_id VARCHAR REFERENCES relationships(id),
  
  -- HAZOP Guide Words
  guide_word VARCHAR CHECK (guide_word IN ('no', 'more', 'less', 'as_well_as', 'part_of', 'reverse', 'other_than', 'early', 'late', 'before', 'after')),
  
  -- Deviation analysis
  parameter VARCHAR NOT NULL,  -- What is deviating
  deviation_description TEXT,
  
  -- Consequences
  consequences JSONB,
  /* Example:
  {
    "immediate": ["authentication_bypass", "data_corruption"],
    "cascading": ["service_unavailable", "trust_erosion"],
    "worst_case": "complete_system_compromise"
  }
  */
  
  -- Causes
  causes JSONB,
  /* Example:
  {
    "technical": ["network_latency", "buffer_overflow"],
    "human": ["misconfiguration", "training_gap"],
    "environmental": ["power_fluctuation", "extreme_load"]
  }
  */
  
  -- Safeguards
  existing_safeguards TEXT[],
  recommended_safeguards TEXT[],
  
  severity VARCHAR CHECK (severity IN ('negligible', 'minor', 'moderate', 'major', 'catastrophic')),
  likelihood VARCHAR CHECK (likelihood IN ('rare', 'unlikely', 'possible', 'likely', 'certain')),
  
  created_at TIMESTAMP DEFAULT NOW()
);

-- Link HAZOP deviations to UCAs
CREATE TABLE hazop_uca_mapping (
  hazop_id VARCHAR REFERENCES hazop_deviations(id),
  analysis_id VARCHAR REFERENCES analyses(id),
  correlation_strength VARCHAR CHECK (correlation_strength IN ('weak', 'moderate', 'strong')),
  notes TEXT,
  PRIMARY KEY (hazop_id, analysis_id)
);
```

## Business Context Integration (PASTA Enhancement)

### Business-Driven Threat Modeling
```sql
-- Extend system_definition with PASTA business context
ALTER TABLE system_definition ADD COLUMN business_context JSONB;
/* Example:
{
  "business_objectives": {
    "primary": ["increase_revenue_20%", "reduce_fraud_50%"],
    "compliance": ["maintain_pci_dss", "achieve_soc2"],
    "strategic": ["market_expansion", "ai_transformation"]
  },
  "threat_intelligence": {
    "industry_threats": ["ransomware_epidemic", "supply_chain_attacks"],
    "targeted_campaigns": ["apt28_banking", "carbanak"],
    "threat_landscape_score": 8.5
  },
  "risk_appetite": {
    "financial": "moderate",
    "operational": "low",
    "reputational": "very_low",
    "compliance": "zero_tolerance"
  }
}
*/

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
```

## Integrated Analysis Views

### Comprehensive Security Posture
```sql
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
```

### AI Agent Risk Assessment
```sql
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
```

### Cross-Framework Validation
```sql
CREATE FUNCTION validate_cross_framework_consistency() RETURNS TABLE(
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
```

## Threat Intelligence Integration

### Dynamic Threat Landscape Tracking
```sql
-- Track evolving threats, especially important for AI/ML
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
```

### AI Capability Evolution Tracking
```sql
-- Track how AI capabilities change and new risks emerge
ALTER TABLE ai_agent_layers ADD COLUMN capability_evolution JSONB;
/* Example:
{
  "version_history": [
    {
      "version": "1.0",
      "date": "2024-01-01",
      "capabilities_added": ["tool_use", "web_browsing"],
      "capabilities_removed": [],
      "new_risks": ["data_exfiltration", "autonomous_action"]
    },
    {
      "version": "2.0",
      "date": "2024-06-01",
      "capabilities_added": ["long_term_memory", "self_modification"],
      "capabilities_removed": ["supervised_only"],
      "new_risks": ["goal_misalignment", "deceptive_behavior"]
    }
  ],
  "current_trajectory": "increasing_autonomy",
  "risk_trend": "escalating",
  "recommended_controls_update": ["human_oversight", "capability_limits"]
}
*/
```

## Executive Decision Support

### Security Investment Optimization
```sql
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
    WHEN roi_percentage > 300 AND complexity_score <= 3 THEN 'immediate'
    WHEN roi_percentage > 200 OR regulations_addressed > 2 THEN 'high'
    WHEN roi_percentage > 100 THEN 'medium'
    ELSE 'low'
  END as implementation_priority

FROM investment_analysis
ORDER BY roi_percentage DESC NULLS LAST, total_risk_reduced DESC;
```

### Regulatory Compliance Automation
```sql
-- Compliance requirements tracking
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

-- Automated compliance status view
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
         CARDINALITY(ARRAY(SELECT DISTINCT jsonb_array_elements_text(cr.required_controls->'data_protection')))::FLOAT >= 0.95 
    THEN 'audit_ready'
    WHEN COUNT(DISTINCT im.control_type)::FLOAT / 
         CARDINALITY(ARRAY(SELECT DISTINCT jsonb_array_elements_text(cr.required_controls->'data_protection')))::FLOAT >= 0.80 
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
```

## Implementation Roadmap

### Phase 1: Core Extensions (Weeks 1-3)
1. Implement DREAD scoring for existing scenarios
2. Add HAZOP deviation analysis tables
3. Create basic privacy threat categories
4. **NEW: Set up threat landscape intelligence tables**
5. **NEW: Implement automated threat feed integration**

### Phase 2: AI/ML and Business Context (Weeks 4-6)
1. Implement MAESTRO agent layers
2. Add PASTA business context integration
3. Create unified risk scoring system

### Phase 3: Advanced Integration (Weeks 7-8)
1. Build cross-framework validation
2. Create executive dashboards
3. Implement AI agent orchestration

## Key Benefits of STPA-Sec+

1. **Comprehensive Coverage**: Addresses security, privacy, AI/ML, and business risks
2. **Quantitative Analysis**: Multiple scoring systems for different stakeholder needs
3. **AI-Ready**: Built for the reality that AI will be in every system
4. **Privacy-First**: GDPR/CCPA compliance built into the methodology
5. **Executive-Friendly**: Business impact and ROI calculations throughout
6. **Systematic**: Guide words and structured analysis prevent blind spots
7. **Evidence-Based**: PASTA's emphasis on threat intelligence and validation

This enhanced framework positions STPA-Sec+ as the most comprehensive security analysis methodology available, uniquely suited for modern AI-integrated systems while maintaining the systems thinking foundation that makes STPA-Sec so powerful.