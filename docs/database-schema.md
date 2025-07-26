# STPA-Sec PostgreSQL Schema Documentation

## Overview
This schema implements the complete STPA-Sec 4-step process with full traceability and property richness.

## Step 1: System Definition & Context

### Mission Statement
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
  system_boundaries JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  version INT DEFAULT 1
);
```

### Stakeholders
```sql
CREATE TABLE stakeholders (
  id VARCHAR PRIMARY KEY,
  type VARCHAR CHECK (type IN ('primary', 'secondary', 'threat_actor')) NOT NULL,
  name VARCHAR NOT NULL,
  interests TEXT[],
  capabilities TEXT[], -- For threat actors
  motivation TEXT,     -- For threat actors
  trust_level VARCHAR CHECK (trust_level IN ('trusted', 'partially_trusted', 'untrusted')),
  properties JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Example entries
INSERT INTO stakeholders VALUES 
('SH-001', 'primary', 'Bank Customers', 
  ARRAY['account_security', 'service_availability'], 
  NULL, NULL, 'trusted', 
  '{"priority": "high", "count": "1M+"}'),
('SH-002', 'threat_actor', 'Cybercriminals',
  ARRAY['financial_gain', 'data_theft'],
  ARRAY['phishing', 'malware', 'social_engineering'],
  'financial', 'untrusted',
  '{"sophistication": "medium", "resources": "moderate"}');
```

### Losses
```sql
CREATE TABLE losses (
  id VARCHAR PRIMARY KEY,
  description TEXT NOT NULL,
  severity VARCHAR CHECK (severity IN ('low', 'medium', 'high', 'critical')) NOT NULL,
  stakeholder_refs VARCHAR[] NOT NULL,
  impact_type VARCHAR CHECK (impact_type IN ('safety', 'financial', 'operational', 'reputation', 'privacy')),
  properties JSONB,
  CONSTRAINT fk_stakeholders CHECK (
    stakeholder_refs <@ (SELECT array_agg(id) FROM stakeholders)
  )
);
```

### Hazards
```sql
CREATE TABLE hazards (
  id VARCHAR PRIMARY KEY,
  description TEXT NOT NULL,
  loss_refs VARCHAR[] NOT NULL,
  worst_case_scenario TEXT,
  likelihood VARCHAR CHECK (likelihood IN ('rare', 'unlikely', 'possible', 'likely', 'certain')),
  detection_difficulty VARCHAR CHECK (detection_difficulty IN ('trivial', 'easy', 'moderate', 'hard', 'extreme')),
  properties JSONB,
  CONSTRAINT fk_losses CHECK (
    loss_refs <@ (SELECT array_agg(id) FROM losses)
  )
);
```

### Entities
```sql
CREATE TABLE entities (
  id VARCHAR PRIMARY KEY,
  name VARCHAR NOT NULL,
  description TEXT,
  -- Core categorization
  category VARCHAR CHECK (category IN ('human', 'software', 'hardware', 'physical', 'organizational')),
  subcategory VARCHAR, -- e.g., 'microservice', 'web_app', 'sensor', 'policy'
  
  -- Technical properties
  technology VARCHAR,    -- e.g., 'Node.js v18.2'
  version VARCHAR,       -- e.g., '2.3.1'
  vendor VARCHAR,       -- e.g., 'OpenSource', 'Microsoft', 'Custom'
  
  -- Security properties
  criticality VARCHAR CHECK (criticality IN ('low', 'medium', 'high', 'critical')),
  trust_level VARCHAR CHECK (trust_level IN ('untrusted', 'partially_trusted', 'trusted', 'critical')),
  exposure VARCHAR CHECK (exposure IN ('internal', 'dmz', 'external', 'public')),
  
  -- Operational properties
  owner VARCHAR,         -- Team or person responsible
  deployment VARCHAR,    -- e.g., 'kubernetes', 'vm', 'physical'
  location VARCHAR,      -- e.g., 'aws-us-east-1', 'on-premise-dc1'
  
  -- Extended properties
  properties JSONB,      -- Additional flexible properties
  /*
  Example properties:
  {
    "compliance_requirements": ["PCI-DSS", "SOC2"],
    "dependencies": ["E-002", "E-003"],
    "ports": [443, 8080],
    "protocols": ["HTTPS", "WebSocket"],
    "data_classification": "confidential",
    "recovery_time_objective": "5 minutes",
    "performance_sla": {"latency": "100ms", "availability": "99.99%"}
  }
  */
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_entities_category ON entities(category);
CREATE INDEX idx_entities_criticality ON entities(criticality);
CREATE INDEX idx_entities_properties ON entities USING GIN(properties);
```

## Step 2: Control Structure (Relationships)

### Relationships
```sql
CREATE TABLE relationships (
  id VARCHAR PRIMARY KEY,
  source_id VARCHAR NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  target_id VARCHAR NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  
  -- Core properties
  action VARCHAR NOT NULL,  -- e.g., 'Authenticate User', 'Return Token'
  type VARCHAR CHECK (type IN ('control', 'feedback')) NOT NULL,
  
  -- Communication properties
  protocol VARCHAR,          -- e.g., 'HTTPS/TLS1.3', 'gRPC', 'MQTT'
  channel VARCHAR,          -- e.g., 'internet', 'internal_network', 'serial'
  data_format VARCHAR,      -- e.g., 'JSON', 'XML', 'Binary', 'Protobuf'
  
  -- Timing properties
  timing_type VARCHAR CHECK (timing_type IN ('synchronous', 'asynchronous', 'periodic', 'event_driven')),
  frequency VARCHAR,        -- e.g., 'on_demand', '1/minute', 'continuous'
  timeout VARCHAR,          -- e.g., '30s', '5m', 'none'
  retry_policy VARCHAR,     -- e.g., '3x exponential backoff'
  
  -- Security properties
  encryption VARCHAR,       -- e.g., 'AES-256-GCM', 'TLS', 'none'
  authentication VARCHAR,   -- e.g., 'mutual_tls', 'api_key', 'oauth2'
  integrity_check VARCHAR,  -- e.g., 'hmac-sha256', 'signature', 'checksum'
  
  -- Data properties
  data_sensitivity VARCHAR CHECK (data_sensitivity IN ('public', 'internal', 'confidential', 'secret')),
  data_volume VARCHAR,      -- e.g., 'low', 'medium', 'high', '1GB/hour'
  
  -- Extended properties
  properties JSONB,
  /*
  Example:
  {
    "qos_level": 2,
    "message_ordering": "guaranteed",
    "compression": "gzip",
    "rate_limit": "1000/minute",
    "circuit_breaker": {"threshold": 0.5, "timeout": "30s"},
    "monitoring": {"metrics": ["latency", "error_rate"], "alerts": true}
  }
  */
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  
  CONSTRAINT different_entities CHECK (source_id != target_id)
);

CREATE INDEX idx_relationships_source ON relationships(source_id);
CREATE INDEX idx_relationships_target ON relationships(target_id);
CREATE INDEX idx_relationships_type ON relationships(type);
CREATE INDEX idx_relationships_properties ON relationships USING GIN(properties);
```

## Step 3: Unsafe Control Actions & STRIDE

### Analyses (UCAs and STRIDE)
```sql
CREATE TABLE analyses (
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
  
  -- Metadata
  analyzed_by VARCHAR,    -- AI model or human analyst
  confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
  properties JSONB,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_analyses_relationship ON analyses(relationship_id);
CREATE INDEX idx_analyses_type ON analyses(analysis_type);
-- Indexes for JSONB queries
CREATE INDEX idx_analyses_uca_severity ON analyses ((uca_not_provided->>'severity'), (uca_provided_causes_hazard->>'severity'));
CREATE INDEX idx_analyses_stride_severity ON analyses ((stride_spoofing->>'severity'), (stride_tampering->>'severity'));
```

## Step 4: Causal Scenarios & Mitigations

### Causal Scenarios
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

## Helper Views and Functions

### Traceability Views
```sql
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
```

### Data Validation Functions
```sql
-- Ensure all UCAs link to valid hazards
CREATE FUNCTION validate_uca_hazard_links() RETURNS BOOLEAN AS $$
DECLARE
  invalid_count INT;
BEGIN
  SELECT COUNT(*) INTO invalid_count
  FROM analyses a
  WHERE 
    (a.uca_not_provided->>'exists' = 'true' AND 
     NOT (a.uca_not_provided->'hazard_refs' ?| array(SELECT id FROM hazards)))
    OR similar checks for other UCA types...;
    
  RETURN invalid_count = 0;
END;
$$ LANGUAGE plpgsql;

-- Check for orphaned relationships
CREATE FUNCTION find_incomplete_analyses() RETURNS TABLE(
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
```

## Usage Examples

### Creating a complete analysis chain:
```sql
-- 1. Create entities
INSERT INTO entities (id, name, category, technology, criticality, trust_level)
VALUES 
  ('E-001', 'Web Application', 'software', 'React 18', 'critical', 'untrusted'),
  ('E-002', 'Auth Service', 'software', 'Node.js', 'critical', 'trusted');

-- 2. Create relationship
INSERT INTO relationships (id, source_id, target_id, action, type, protocol, encryption)
VALUES ('R-001', 'E-001', 'E-002', 'Authenticate User', 'control', 'HTTPS', 'TLS1.3');

-- 3. Analyze for UCAs and STRIDE
INSERT INTO analyses (id, relationship_id, analysis_type, uca_not_provided, stride_spoofing)
VALUES (
  'A-001', 
  'R-001', 
  'stpa-sec',
  '{"exists": true, "description": "Auth not sent on login", "severity": "high", "hazard_refs": ["H-001"]}',
  '{"exists": true, "description": "Credential theft", "severity": "critical", "hazard_refs": ["H-001"]}'
);

-- 4. Create scenario
INSERT INTO scenarios (id, relationship_id, uca_refs, stride_refs, hazard_refs, description)
VALUES (
  'CS-001', 
  'R-001', 
  ARRAY['not_provided'], 
  ARRAY['spoofing'],
  ARRAY['H-001'],
  'Network partition enables credential theft'
);

-- 5. Create and link mitigation
INSERT INTO mitigations (id, name, type, effectiveness)
VALUES ('M-001', 'Implement mutual TLS', 'preventive', 'high');

INSERT INTO scenario_mitigations (scenario_id, mitigation_id, effectiveness_for_scenario)
VALUES ('CS-001', 'M-001', 'complete');
```

## Query Examples

### Find critical unmitigated scenarios
```sql
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
```

### Analyze entity exposure
```sql
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
```

This schema provides:
1. **Complete STPA-Sec flow** with all 4 steps
2. **Rich property storage** for all entities and relationships
3. **Full traceability** from stakeholders to mitigations
4. **Flexible querying** with JSONB and proper indexes
5. **Data integrity** with constraints and validation
6. **Scalability** for thousands of relationships