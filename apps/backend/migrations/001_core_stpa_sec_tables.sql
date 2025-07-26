-- STPA-Sec+ Core Tables Migration
-- Phase 1: Core Implementation (Weeks 1-2)
-- This migration creates the foundational tables for STPA-Sec analysis

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Step 1: System Definition & Context
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
  
  -- Mission criticality assessment
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
  
  -- PASTA business context integration
  business_context JSONB,
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
  
  created_at TIMESTAMP DEFAULT NOW(),
  version INT DEFAULT 1
);

-- Stakeholders (including threat actors)
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

-- Enhanced Adversary Modeling
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

-- Control Loops
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
  
  -- Process Model Validation
  model_validation JSONB,
  /* Example:
  {
    "last_validated": "2024-01-15",
    "accuracy_metrics": {"state_prediction": 0.95, "timing_prediction": 0.87},
    "drift_indicators": ["increased_timeout_frequency", "unexpected_state_transitions"],
    "validation_method": "historical_comparison",
    "next_validation_due": "2024-02-15"
  }
  */
  
  properties JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Losses
CREATE TABLE losses (
  id VARCHAR PRIMARY KEY,
  description TEXT NOT NULL,
  severity VARCHAR CHECK (severity IN ('low', 'medium', 'high', 'critical')) NOT NULL,
  stakeholder_refs VARCHAR[] NOT NULL,
  impact_type VARCHAR CHECK (impact_type IN ('safety', 'financial', 'operational', 'reputation', 'privacy')),
  properties JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Hazards
CREATE TABLE hazards (
  id VARCHAR PRIMARY KEY,
  description TEXT NOT NULL,
  loss_refs VARCHAR[] NOT NULL,
  worst_case_scenario TEXT,
  likelihood VARCHAR CHECK (likelihood IN ('rare', 'unlikely', 'possible', 'likely', 'certain')),
  detection_difficulty VARCHAR CHECK (detection_difficulty IN ('trivial', 'easy', 'moderate', 'hard', 'extreme')),
  properties JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Entities
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
  
  -- AI/ML properties for MAESTRO integration
  ai_properties JSONB,
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

-- Create indexes for performance
CREATE INDEX idx_entities_category ON entities(category);
CREATE INDEX idx_entities_criticality ON entities(criticality);
CREATE INDEX idx_entities_properties ON entities USING GIN(properties);
CREATE INDEX idx_entities_ai_properties ON entities USING GIN(ai_properties);

-- Relationships (Control Structure)
CREATE TABLE relationships (
  id VARCHAR PRIMARY KEY,
  source_id VARCHAR NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  target_id VARCHAR NOT NULL REFERENCES entities(id) ON DELETE CASCADE,
  
  -- Core properties
  action VARCHAR NOT NULL,  -- e.g., 'Authenticate User', 'Return Token'
  type VARCHAR CHECK (type IN ('control', 'feedback')) NOT NULL,
  
  -- Control loop context
  control_loop_id VARCHAR REFERENCES control_loops(id),
  operational_modes JSONB,
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

-- Create indexes for relationships
CREATE INDEX idx_relationships_source ON relationships(source_id);
CREATE INDEX idx_relationships_target ON relationships(target_id);
CREATE INDEX idx_relationships_type ON relationships(type);
CREATE INDEX idx_relationships_control_loop ON relationships(control_loop_id);
CREATE INDEX idx_relationships_properties ON relationships USING GIN(properties);

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

-- Helper function to validate stakeholder references
CREATE OR REPLACE FUNCTION validate_stakeholder_refs() 
RETURNS TRIGGER AS $$
BEGIN
  -- Check if all stakeholder references exist
  IF NOT (NEW.stakeholder_refs <@ (SELECT array_agg(id) FROM stakeholders)) THEN
    RAISE EXCEPTION 'Invalid stakeholder reference in stakeholder_refs';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Helper function to validate loss references
CREATE OR REPLACE FUNCTION validate_loss_refs() 
RETURNS TRIGGER AS $$
BEGIN
  -- Check if all loss references exist
  IF NOT (NEW.loss_refs <@ (SELECT array_agg(id) FROM losses)) THEN
    RAISE EXCEPTION 'Invalid loss reference in loss_refs';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add triggers for referential integrity
CREATE TRIGGER check_stakeholder_refs
  BEFORE INSERT OR UPDATE ON losses
  FOR EACH ROW
  EXECUTE FUNCTION validate_stakeholder_refs();

CREATE TRIGGER check_loss_refs
  BEFORE INSERT OR UPDATE ON hazards
  FOR EACH ROW
  EXECUTE FUNCTION validate_loss_refs();