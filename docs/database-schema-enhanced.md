# Enhanced STPA-Sec PostgreSQL Schema Documentation

## Overview
This enhanced schema incorporates feedback to better align with STPA-Sec methodology, particularly strengthening control loop modeling, temporal context, adversary modeling, and wargaming support.

## Enhanced Step 1: System Definition & Context

### Mission Statement (Enhanced)
```sql
CREATE TABLE system_definition (
  id VARCHAR PRIMARY KEY DEFAULT 'system-001',
  mission_statement JSONB NOT NULL,
  /* Example:
  {
    "purpose": "Enable secure digital banking transactions",
    "method": "Multi-factor authentication and encrypted communications",
    "goals": ["Protect customer assets", "Ensure 24/7 availability", "Maintain regulatory compliance"],
    "constraints": ["PCI-DSS compliance", "Sub-100ms latency", "Zero customer data exposure"]
  }
  */
  
  -- NEW: Mission criticality assessment
  mission_criticality JSONB,
  /* Example:
  {
    "primary_mission": "secure digital banking",
    "success_metrics": {
      "transaction_availability": {"target": "99.99%", "critical_threshold": "99.9%"},
      "data_integrity": {"target": "100%", "critical_threshold": "99.999%"},
      "response_time": {"target": "100ms", "critical_threshold": "1000ms"}
    },
    "failure_impacts": {
      "financial": "Up to $1M per hour downtime",
      "reputation": "Customer trust erosion",
      "regulatory": "Potential license suspension"
    },
    "mission_dependencies": ["authentication_service", "transaction_processor", "data_storage"]
  }
  */
  
  system_boundaries JSONB,
  operational_context JSONB,
  /* Example:
  {
    "deployment_environments": ["production", "staging", "disaster_recovery"],
    "geographic_scope": ["US", "EU", "APAC"],
    "regulatory_jurisdictions": ["US-Federal", "EU-GDPR", "CA-PIPEDA"],
    "integration_points": ["third_party_payment", "credit_bureaus", "regulatory_reporting"]
  }
  */
  
  created_at TIMESTAMP DEFAULT NOW(),
  version INT DEFAULT 1
);
```

### Enhanced Adversary Modeling
```sql
-- Separate adversary modeling from general stakeholders
CREATE TABLE adversaries (
  id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  type VARCHAR CHECK (type IN ('nation_state', 'organized_crime', 'hacktivist', 'insider', 'opportunist')),
  
  -- Capabilities assessment
  technical_sophistication VARCHAR CHECK (technical_sophistication IN ('low', 'medium', 'high', 'advanced')),
  resources VARCHAR CHECK (resources IN ('minimal', 'moderate', 'significant', 'unlimited')),
  
  -- Detailed capability breakdown
  capabilities JSONB,
  /* Example:
  {
    "attack_vectors": ["phishing", "zero_day", "supply_chain", "physical"],
    "tools": ["custom_malware", "commercial_exploits", "open_source_tools"],
    "persistence": "high",
    "stealth": "advanced",
    "attribution_difficulty": "extreme"
  }
  */
  
  -- Motivations and objectives
  primary_motivation VARCHAR CHECK (primary_motivation IN ('financial', 'espionage', 'disruption', 'ideology', 'personal')),
  objectives TEXT[],
  
  -- Behavioral patterns
  ttps JSONB, -- Tactics, Techniques, and Procedures
  /* Example:
  {
    "initial_access": ["spear_phishing", "supply_chain_compromise"],
    "execution": ["powershell", "scheduled_tasks"],
    "persistence": ["registry_keys", "startup_folder"],
    "defense_evasion": ["obfuscation", "process_injection"],
    "exfiltration": ["https", "dns_tunneling"]
  }
  */
  
  -- Historical context
  known_campaigns TEXT[],
  target_sectors TEXT[],
  
  properties JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Link adversaries to their control problems
CREATE TABLE adversary_control_problems (
  adversary_id VARCHAR REFERENCES adversaries(id),
  entity_id VARCHAR REFERENCES entities(id),
  control_capability JSONB,
  /* Example:
  {
    "can_observe": ["network_traffic", "error_messages"],
    "can_influence": ["input_data", "timing"],
    "can_disrupt": ["availability", "integrity"],
    "constraints": ["no_physical_access", "limited_time_window"]
  }
  */
  PRIMARY KEY (adversary_id, entity_id)
);
```

## Enhanced Step 2: Control Structure

### Control Loops
```sql
CREATE TABLE control_loops (
  id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  purpose TEXT,
  
  -- Control loop components
  controlled_process VARCHAR NOT NULL,
  control_algorithm TEXT,
  
  -- Process model (controller's understanding)
  process_model JSONB,
  /* Example:
  {
    "assumed_state": {"authenticated": false, "session_active": false},
    "state_update_sources": ["auth_response", "session_timeout"],
    "update_frequency": "event_driven",
    "staleness_tolerance": "5_minutes"
  }
  */
  
  -- Control loop timing
  loop_frequency VARCHAR,
  max_loop_delay VARCHAR,
  
  properties JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Enhanced relationships with control loop context
ALTER TABLE relationships ADD COLUMN control_loop_id VARCHAR REFERENCES control_loops(id);
ALTER TABLE relationships ADD COLUMN operational_modes JSONB;
/* Example operational_modes:
{
  "normal": {
    "conditions": ["all_services_healthy", "load < 80%"],
    "constraints": ["standard_timeout", "normal_retry_policy"]
  },
  "degraded": {
    "conditions": ["some_services_down", "load > 80%"],
    "constraints": ["extended_timeout", "aggressive_caching"]
  },
  "emergency": {
    "conditions": ["critical_service_failure", "suspected_attack"],
    "constraints": ["bypass_non_critical", "lockdown_mode"]
  }
}
*/
```

## Enhanced Step 3: Context-Aware UCAs

### Enhanced Analyses with Temporal Context
```sql
ALTER TABLE analyses ADD COLUMN temporal_context JSONB;
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

ALTER TABLE analyses ADD COLUMN adversarial_context JSONB;
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

-- Process Model Validation
ALTER TABLE control_loops ADD COLUMN model_validation JSONB;
/* Example:
{
  "last_validated": "2024-01-15",
  "accuracy_metrics": {"state_prediction": 0.95, "timing_prediction": 0.87},
  "drift_indicators": ["increased_timeout_frequency", "unexpected_state_transitions"],
  "validation_method": "historical_comparison",
  "next_validation_due": "2024-02-15"
}
*/
```

## Step 4: Causal Scenarios & Mitigations

### Causal Scenarios with D4 Assessment
```sql
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

CREATE INDEX idx_scenarios_relationship ON scenarios(relationship_id);
CREATE INDEX idx_scenarios_risk ON scenarios(risk_score DESC);
CREATE INDEX idx_scenarios_d4 ON scenarios((d4_assessment->>'overall_score')::INT DESC);
```

### Mitigations
```sql
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
```

## Enhanced Step 4: Wargaming Integration

### Wargaming Sessions
```sql
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
```

## Enhanced Validation and Analysis Views

### Mission Impact Traceability
```sql
CREATE VIEW mission_impact_analysis AS
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
```

### Adversarial Analysis View
```sql
CREATE VIEW adversary_capability_coverage AS
SELECT 
  a.name as adversary,
  a.type as adversary_type,
  
  -- Attack surface analysis
  COUNT(DISTINCT acp.entity_id) as controlled_entities,
  COUNT(DISTINCT r.id) as influenced_relationships,
  
  -- Defensive coverage
  COUNT(DISTINCT m.id) as applicable_mitigations,
  AVG(m.effectiveness::INT) as avg_mitigation_effectiveness,
  
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
```

### Temporal Risk View
```sql
CREATE VIEW temporal_risk_windows AS
SELECT 
  tc.time_window,
  tc.window_type,
  COUNT(DISTINCT a.id) as active_vulnerabilities,
  MAX(a.risk_score) as peak_risk,
  ARRAY_AGG(DISTINCT a.description) as critical_scenarios

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
```

### D4 Analysis View
```sql
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
```

## Implementation Phases

### Phase 1: Core Implementation
1. Implement base schema (from original document)
2. Add basic adversary modeling
3. Implement control loop tracking

### Phase 2: Enhanced Context
1. Add temporal/operational mode enhancements
2. Implement adversarial control problems
3. Enhanced UCA context modeling

### Phase 3: Advanced Features
1. Full wargaming support
2. Mission impact analysis
3. Automated gap detection

This enhanced schema provides:
- **Better control loop representation** for complex system interactions
- **Explicit adversary modeling** aligned with STPA-Sec methodology
- **Temporal context** to capture "when" conditions for UCAs
- **Wargaming integration** for iterative security validation
- **Mission-centric analysis** to align with business objectives
- **D4 assessment integration** for prioritizing scenarios based on detectability, difficulty, damage, and deniability
- **Process model validation** to track controller accuracy over time

## Final Notes

Based on comprehensive review, this schema achieves:
- ⭐⭐⭐⭐⭐ **Mission Focus**: Explicit mission criticality modeling enables quantitative mission risk assessment
- ⭐⭐⭐⭐⭐ **Adversary Modeling**: Sophisticated adversary control problems capture STPA-Sec's "adversaries solving their own control problem"
- ⭐⭐⭐⭐⭐ **Control Loops**: Process model tracking captures core STPA concept of controller decisions based on potentially stale/incorrect models
- ⭐⭐⭐⭐⭐ **Temporal Context**: Operational modes directly address "when" conditions that make control actions unsafe
- ⭐⭐⭐⭐⭐ **Wargaming**: Move-by-move tracking operationalizes STPA-Sec validation methodology
- ⭐⭐⭐⭐⭐ **Analytics**: Mission impact and adversarial coverage views enable strategic security discussions

This schema serves as a reference implementation for operationalizing STPA-Sec in production environments, bridging academic methodology with practical security engineering requirements.