-- STPA-Sec+ Analysis Tables Migration
-- Phase 1: Core Implementation (Weeks 1-2) - Part 2
-- This migration creates the analysis tables for UCAs, STRIDE, scenarios, and mitigations

-- Step 3: Unsafe Control Actions & STRIDE
CREATE TABLE stpa_analyses (
  id VARCHAR PRIMARY KEY,
  relationship_id VARCHAR NOT NULL REFERENCES relationships(id) ON DELETE CASCADE,
  analysis_type VARCHAR CHECK (analysis_type IN ('stpa-sec', 'stride', 'pasta', 'maestro')) NOT NULL,
  
  -- UCA Analysis (for STPA-Sec)
  uca_not_provided JSONB,
  /*
  {
    "exists": true,
    "description": "Authentication request not sent when user needs access",
    "context": "Network failure or service unavailable",
    "severity": "high",
    "hazard_refs": ["H-001", "H-003"]
  }
  */
  uca_provided_causes_hazard JSONB,
  uca_wrong_timing JSONB,
  uca_stopped_too_soon JSONB,
  
  -- STRIDE Analysis
  stride_spoofing JSONB,
  /*
  {
    "exists": true,
    "description": "Attacker can spoof authentication requests",
    "attack_vector": "Man-in-the-middle",
    "severity": "critical",
    "hazard_refs": ["H-001"],
    "cves": ["CVE-2023-1234", "CVE-2023-5678"],
    "cwe": ["CWE-287", "CWE-290"]
  }
  */
  stride_tampering JSONB,
  stride_repudiation JSONB,
  stride_information_disclosure JSONB,
  stride_denial_of_service JSONB,
  stride_elevation_of_privilege JSONB,
  
  -- Temporal context for enhanced UCAs
  temporal_context JSONB,
  /* Example:
  {
    "timing_windows": {
      "critical": ["market_hours", "end_of_month"],
      "sensitive": ["maintenance_window", "shift_change"]
    },
    "sequences": {
      "prerequisite_actions": ["user_login", "mfa_complete"],
      "concurrent_actions": ["parallel_transactions"],
      "follow_up_actions": ["audit_log", "notification"]
    },
    "state_dependencies": {
      "system_state": ["normal_operation", "high_load"],
      "environmental_state": ["business_hours", "holiday"]
    }
  }
  */
  
  -- Adversarial context
  adversarial_context JSONB,
  /* Example:
  {
    "adversary_control": {
      "observability": ["can_see_responses", "timing_information"],
      "influence": ["can_inject_commands", "can_delay_messages"],
      "exploitation_window": "during_authentication"
    },
    "defensive_assumptions": [
      "adversary_has_network_position",
      "adversary_knows_protocol"
    ]
  }
  */
  
  -- DREAD Assessment integration
  dread_assessment JSONB,
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
  
  -- Metadata
  analyzed_by VARCHAR,    -- AI model or human analyst
  confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
  properties JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for analyses
CREATE INDEX idx_analyses_relationship ON analyses(relationship_id);
CREATE INDEX idx_analyses_type ON analyses(analysis_type);
-- Indexes for JSONB queries
CREATE INDEX idx_analyses_uca_severity ON analyses ((uca_not_provided->>'severity'), (uca_provided_causes_hazard->>'severity'));
CREATE INDEX idx_analyses_stride_severity ON analyses ((stride_spoofing->>'severity'), (stride_tampering->>'severity'));
CREATE INDEX idx_analyses_dread_score ON analyses (CAST(dread_assessment->>'total_score' AS INT));

-- Step 4: Causal Scenarios
CREATE TABLE scenarios (
  id VARCHAR PRIMARY KEY,
  relationship_id VARCHAR REFERENCES relationships(id) ON DELETE CASCADE,
  
  -- Links to analyses
  uca_refs VARCHAR[],      -- Can reference multiple UCAs
  stride_refs VARCHAR[],   -- Can reference multiple STRIDE categories
  hazard_refs VARCHAR[] NOT NULL,  -- Must link to hazards
  threat_actor_refs VARCHAR[],     -- Which actors could execute
  
  -- Scenario details
  description TEXT NOT NULL,
  attack_chain TEXT[],     -- Step-by-step attack sequence
  prerequisites TEXT[],    -- What must be true for scenario
  
  -- Risk assessment
  likelihood VARCHAR CHECK (likelihood IN ('rare', 'unlikely', 'possible', 'likely', 'certain')),
  impact VARCHAR CHECK (impact IN ('negligible', 'minor', 'moderate', 'major', 'catastrophic')),
  risk_score FLOAT GENERATED ALWAYS AS (
    CASE 
      WHEN likelihood = 'rare' THEN 1
      WHEN likelihood = 'unlikely' THEN 2
      WHEN likelihood = 'possible' THEN 3
      WHEN likelihood = 'likely' THEN 4
      WHEN likelihood = 'certain' THEN 5
    END *
    CASE
      WHEN impact = 'negligible' THEN 1
      WHEN impact = 'minor' THEN 2
      WHEN impact = 'moderate' THEN 3
      WHEN impact = 'major' THEN 4
      WHEN impact = 'catastrophic' THEN 5
    END
  ) STORED,
  
  -- D4 Assessment (Detectability, Difficulty, Damage, Deniability)
  d4_assessment JSONB,
  /* Example:
  {
    "detectability": {"score": 3, "rationale": "Logs available but require correlation"},
    "difficulty": {"score": 4, "rationale": "Requires insider knowledge"},
    "damage": {"score": 5, "rationale": "Complete mission failure"},
    "deniability": {"score": 2, "rationale": "Clear attribution possible"},
    "overall_score": 14,
    "priority": "high"
  }
  */
  
  -- Contributing factors
  contributing_factors JSONB,
  /*
  {
    "technical": ["weak_authentication", "unencrypted_channel"],
    "procedural": ["no_security_training", "shared_credentials"],
    "environmental": ["public_wifi", "physical_access"]
  }
  */
  
  properties JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for scenarios
CREATE INDEX idx_scenarios_relationship ON scenarios(relationship_id);
CREATE INDEX idx_scenarios_risk ON scenarios(risk_score DESC);
CREATE INDEX idx_scenarios_d4 ON scenarios(CAST(d4_assessment->>'overall_score' AS INT) DESC);

-- Mitigations
CREATE TABLE mitigations (
  id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  description TEXT NOT NULL,
  
  -- Categorization
  type VARCHAR CHECK (type IN ('preventive', 'detective', 'corrective', 'compensating')),
  category VARCHAR CHECK (category IN ('technical', 'procedural', 'physical', 'administrative')),
  
  -- Effectiveness
  effectiveness VARCHAR CHECK (effectiveness IN ('low', 'medium', 'high', 'very_high')),
  implementation_difficulty VARCHAR CHECK (implementation_difficulty IN ('trivial', 'easy', 'moderate', 'hard', 'extreme')),
  
  -- Cost analysis
  cost_estimate JSONB,
  /*
  {
    "initial": {"amount": 50000, "currency": "USD"},
    "recurring": {"amount": 5000, "currency": "USD", "period": "monthly"},
    "resources": {"developers": 2, "time": "3 months"}
  }
  */
  
  -- Implementation details
  implementation_steps TEXT[],
  requirements TEXT[],      -- Prerequisites for implementation
  side_effects TEXT[],      -- Potential negative impacts
  
  properties JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Many-to-many relationship for scenarios and mitigations
CREATE TABLE scenario_mitigations (
  scenario_id VARCHAR REFERENCES scenarios(id) ON DELETE CASCADE,
  mitigation_id VARCHAR REFERENCES mitigations(id) ON DELETE CASCADE,
  
  -- How well this mitigation addresses this specific scenario
  effectiveness_for_scenario VARCHAR CHECK (effectiveness_for_scenario IN ('partial', 'substantial', 'complete')),
  implementation_priority INT CHECK (implementation_priority BETWEEN 1 AND 10),
  notes TEXT,
  
  PRIMARY KEY (scenario_id, mitigation_id)
);

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
  
  -- AI Capability Evolution Tracking
  capability_evolution JSONB,
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
  
  PRIMARY KEY (agent_id, layer_type)
);

-- HAZOP Deviations
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

-- Helper function to validate hazard references
CREATE OR REPLACE FUNCTION validate_hazard_refs() 
RETURNS TRIGGER AS $$
BEGIN
  -- Check if all hazard references exist
  IF NOT (NEW.hazard_refs <@ (SELECT array_agg(id) FROM hazards)) THEN
    RAISE EXCEPTION 'Invalid hazard reference in hazard_refs';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add trigger for scenarios
CREATE TRIGGER check_hazard_refs
  BEFORE INSERT OR UPDATE ON scenarios
  FOR EACH ROW
  EXECUTE FUNCTION validate_hazard_refs();

-- Unified risk scoring across frameworks
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