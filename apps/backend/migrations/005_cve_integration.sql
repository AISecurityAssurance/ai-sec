-- STPA-Sec+ CVE Integration Migration
-- Phase 1: CVE Database and Contextual Risk Scoring

-- CVE Database with enriched metadata
CREATE TABLE cve_database (
  cve_id VARCHAR PRIMARY KEY,  -- CVE-2024-12345
  published_date DATE NOT NULL,
  last_modified DATE NOT NULL,
  
  -- Vulnerability details
  description TEXT NOT NULL,
  vulnerability_type VARCHAR[],  -- ['buffer_overflow', 'sql_injection', etc.]
  attack_vector VARCHAR CHECK (attack_vector IN ('network', 'adjacent', 'local', 'physical')),
  attack_complexity VARCHAR CHECK (attack_complexity IN ('low', 'high')),
  privileges_required VARCHAR CHECK (privileges_required IN ('none', 'low', 'high')),
  user_interaction VARCHAR CHECK (user_interaction IN ('none', 'required')),
  
  -- Scoring
  cvss_v3_score FLOAT CHECK (cvss_v3_score >= 0 AND cvss_v3_score <= 10),
  cvss_v3_vector VARCHAR,
  cvss_severity VARCHAR CHECK (cvss_severity IN ('none', 'low', 'medium', 'high', 'critical')),
  epss_score FLOAT CHECK (epss_score >= 0 AND epss_score <= 1),  -- Exploit Prediction Scoring System
  
  -- Affected products
  affected_products JSONB,
  /* Example:
  {
    "products": [
      {
        "vendor": "microsoft",
        "product": "windows_server",
        "versions": ["2019", "2022"],
        "version_end_excluding": "2019.0.17",
        "cpe": "cpe:2.3:o:microsoft:windows_server:2019:*:*:*:*:*:*:*"
      }
    ]
  }
  */
  
  -- Threat intelligence
  known_exploited BOOLEAN DEFAULT FALSE,
  exploit_maturity VARCHAR CHECK (exploit_maturity IN ('not_defined', 'unproven', 'proof_of_concept', 'functional', 'high')),
  in_the_wild BOOLEAN DEFAULT FALSE,
  ransomware_campaign BOOLEAN DEFAULT FALSE,
  apt_association VARCHAR[],  -- ['APT28', 'Lazarus', etc.]
  
  -- References and mappings
  cve_references JSONB,
  mitre_attack_techniques VARCHAR[],  -- ['T1055', 'T1059.001', etc.]
  cwe_ids VARCHAR[],  -- ['CWE-79', 'CWE-89', etc.]
  
  -- Metadata
  source VARCHAR DEFAULT 'nvd',  -- 'nvd', 'mitre', 'vendor', 'internal'
  confidence_level FLOAT DEFAULT 1.0,
  
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_cve_published_date ON cve_database(published_date DESC);
CREATE INDEX idx_cve_cvss_score ON cve_database(cvss_v3_score DESC);
CREATE INDEX idx_cve_severity ON cve_database(cvss_severity);
CREATE INDEX idx_cve_exploited ON cve_database(known_exploited) WHERE known_exploited = TRUE;
CREATE INDEX idx_cve_products ON cve_database USING GIN(affected_products);

-- Entity CVE mapping with contextual risk
CREATE TABLE entity_vulnerabilities (
  id VARCHAR PRIMARY KEY DEFAULT gen_random_uuid()::VARCHAR,
  entity_id VARCHAR REFERENCES entities(id) ON DELETE CASCADE,
  cve_id VARCHAR REFERENCES cve_database(cve_id),
  
  -- Discovery context
  discovery_date DATE DEFAULT CURRENT_DATE,
  discovery_method VARCHAR CHECK (discovery_method IN ('scanner', 'sast', 'dast', 'manual', 'threat_intel', 'vendor_advisory')),
  scanner_name VARCHAR,  -- 'nessus', 'qualys', 'rapid7', etc.
  scanner_confidence FLOAT CHECK (scanner_confidence >= 0 AND scanner_confidence <= 1),
  
  -- Vulnerability specifics
  affected_versions VARCHAR[],
  affected_components TEXT[],  -- Specific files, services, or functions
  attack_surface TEXT,  -- Description of how it can be exploited
  
  -- Entity-specific risk factors
  exposed_to_internet BOOLEAN DEFAULT FALSE,
  requires_authentication BOOLEAN DEFAULT TRUE,
  privileged_access BOOLEAN DEFAULT FALSE,
  data_sensitivity_multiplier FLOAT DEFAULT 1.0 CHECK (data_sensitivity_multiplier >= 0.5 AND data_sensitivity_multiplier <= 3.0),
  
  -- Environmental factors
  network_accessibility VARCHAR CHECK (network_accessibility IN ('internal', 'dmz', 'internet', 'air_gapped')),
  adjacent_systems_criticality VARCHAR CHECK (adjacent_systems_criticality IN ('low', 'medium', 'high', 'critical')),
  
  -- Compensating controls
  compensating_controls JSONB,
  /* Example:
  {
    "network_controls": {
      "firewall": {"rules": ["block_external", "allow_specific_ips"], "effectiveness": 0.8},
      "ids_ips": {"enabled": true, "signatures_updated": "2024-01-15", "effectiveness": 0.7},
      "network_segmentation": {"vlan_isolated": true, "effectiveness": 0.9}
    },
    "host_controls": {
      "edr": {"product": "crowdstrike", "enabled": true, "effectiveness": 0.85},
      "patching": {"automated": true, "frequency": "weekly"},
      "hardening": {"cis_benchmark": true, "score": 85}
    },
    "application_controls": {
      "waf": {"enabled": true, "custom_rules": 15, "effectiveness": 0.7},
      "input_validation": {"implemented": true, "coverage": 0.9},
      "secure_coding": {"sast_integrated": true, "issues_fixed": 0.95}
    }
  }
  */
  
  -- Control effectiveness calculation
  compensating_control_score FLOAT GENERATED ALWAYS AS (
    GREATEST(
      COALESCE((compensating_controls->'network_controls'->>'effectiveness')::FLOAT, 0),
      COALESCE((compensating_controls->'host_controls'->>'effectiveness')::FLOAT, 0),
      COALESCE((compensating_controls->'application_controls'->>'effectiveness')::FLOAT, 0)
    ) * 0.5  -- Max 50% risk reduction from controls
  ) STORED,
  
  -- Base risk calculation (before context)
  base_risk_score FLOAT,
  
  -- Mission context
  mission_critical_path BOOLEAN DEFAULT FALSE,
  business_process_impact VARCHAR[],  -- ['payment_processing', 'customer_auth', etc.]
  
  -- Status tracking
  status VARCHAR CHECK (status IN ('open', 'mitigating', 'mitigated', 'accepted', 'false_positive', 'exception')) DEFAULT 'open',
  risk_acceptance_reason TEXT,
  risk_accepted_by VARCHAR,
  risk_acceptance_expiry DATE,
  
  -- Mitigation planning
  mitigation_deadline DATE,
  mitigation_priority VARCHAR CHECK (mitigation_priority IN ('emergency', 'critical', 'high', 'medium', 'low')),
  assigned_to VARCHAR,
  
  -- Audit trail
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  created_by VARCHAR,
  updated_by VARCHAR,
  
  CONSTRAINT unique_entity_cve UNIQUE (entity_id, cve_id)
);

-- Create indexes
CREATE INDEX idx_entity_vuln_status ON entity_vulnerabilities(status) WHERE status = 'open';
CREATE INDEX idx_entity_vuln_entity ON entity_vulnerabilities(entity_id);
CREATE INDEX idx_entity_vuln_priority ON entity_vulnerabilities(mitigation_priority, mitigation_deadline);

-- Function to calculate contextual risk score
CREATE OR REPLACE FUNCTION calculate_contextual_risk_score(
  p_entity_vulnerability_id VARCHAR
) RETURNS FLOAT AS $$
DECLARE
  v_base_score FLOAT;
  v_entity_criticality_mult FLOAT;
  v_exposure_mult FLOAT;
  v_exploit_mult FLOAT;
  v_mission_mult FLOAT;
  v_control_reduction FLOAT;
  v_final_score FLOAT;
BEGIN
  SELECT 
    ev.base_risk_score,
    -- Entity criticality multiplier
    CASE e.criticality 
      WHEN 'critical' THEN 2.0
      WHEN 'high' THEN 1.5
      WHEN 'medium' THEN 1.0
      WHEN 'low' THEN 0.7
      ELSE 1.0
    END,
    -- Exposure multiplier
    CASE 
      WHEN ev.exposed_to_internet AND NOT ev.requires_authentication THEN 3.0
      WHEN ev.exposed_to_internet THEN 2.0
      WHEN e.exposure = 'external' THEN 1.8
      WHEN e.exposure = 'dmz' THEN 1.5
      WHEN e.exposure = 'internal' THEN 1.0
      ELSE 0.8
    END,
    -- Exploit likelihood multiplier
    CASE 
      WHEN cve.known_exploited THEN 3.0
      WHEN cve.in_the_wild THEN 2.5
      WHEN cve.exploit_maturity = 'high' THEN 2.0
      WHEN cve.exploit_maturity = 'functional' THEN 1.5
      WHEN cve.epss_score > 0.7 THEN 1.8
      WHEN cve.epss_score > 0.3 THEN 1.3
      ELSE 1.0
    END,
    -- Mission criticality multiplier
    CASE 
      WHEN ev.mission_critical_path THEN 2.0
      WHEN EXISTS (
        SELECT 1 FROM control_loops cl
        JOIN relationships r ON cl.id = r.control_loop_id
        WHERE r.source_id = e.id OR r.target_id = e.id
      ) THEN 1.5
      ELSE 1.0
    END,
    -- Compensating control reduction
    COALESCE(ev.compensating_control_score, 0)
    
  INTO v_base_score, v_entity_criticality_mult, v_exposure_mult, 
       v_exploit_mult, v_mission_mult, v_control_reduction
  FROM entity_vulnerabilities ev
  JOIN entities e ON ev.entity_id = e.id
  JOIN cve_database cve ON ev.cve_id = cve.cve_id
  WHERE ev.id = p_entity_vulnerability_id;
  
  -- Calculate final score with all factors
  v_final_score := v_base_score * 
                   v_entity_criticality_mult * 
                   v_exposure_mult * 
                   v_exploit_mult * 
                   v_mission_mult *
                   (1 - v_control_reduction);
  
  -- Normalize to 0-100 scale
  RETURN LEAST(v_final_score * 10, 100);
END;
$$ LANGUAGE plpgsql;

-- Add column for contextual risk score (will be populated by trigger)
ALTER TABLE entity_vulnerabilities 
ADD COLUMN contextual_risk_score FLOAT;

-- Create trigger to populate base_risk_score
CREATE OR REPLACE FUNCTION update_base_risk_score()
RETURNS TRIGGER AS $$
BEGIN
  NEW.base_risk_score := (
    SELECT cvss_v3_score 
    FROM cve_database 
    WHERE cve_id = NEW.cve_id
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_base_risk_score
BEFORE INSERT OR UPDATE ON entity_vulnerabilities
FOR EACH ROW
EXECUTE FUNCTION update_base_risk_score();

-- Create trigger to populate contextual_risk_score
CREATE OR REPLACE FUNCTION update_contextual_risk_score()
RETURNS TRIGGER AS $$
BEGIN
  NEW.contextual_risk_score := calculate_contextual_risk_score(NEW.id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_contextual_risk_score
AFTER INSERT OR UPDATE ON entity_vulnerabilities
FOR EACH ROW
EXECUTE FUNCTION update_contextual_risk_score();

-- CVE to Scenario mapping
CREATE TABLE cve_scenario_mappings (
  cve_id VARCHAR REFERENCES cve_database(cve_id),
  scenario_id VARCHAR REFERENCES scenarios(id),
  
  -- How CVE enables the scenario
  enablement_type VARCHAR CHECK (enablement_type IN ('direct_exploit', 'privilege_escalation', 'lateral_movement', 'persistence', 'defense_evasion')),
  
  -- Exploitation details
  exploitation_likelihood VARCHAR CHECK (exploitation_likelihood IN ('confirmed', 'high', 'medium', 'low', 'theoretical')),
  exploitation_impact VARCHAR CHECK (exploitation_impact IN ('critical', 'major', 'moderate', 'minor')),
  
  -- Attack chain details
  attack_chain_position INT,  -- Where in the attack chain this CVE is used
  attack_chain_description TEXT,
  prerequisites_met BOOLEAN DEFAULT FALSE,
  additional_requirements TEXT[],  -- Other conditions needed
  
  -- Evidence
  evidence_source VARCHAR,  -- 'threat_intel', 'pen_test', 'incident', 'research'
  evidence_date DATE,
  confidence_level FLOAT DEFAULT 0.5,
  
  PRIMARY KEY (cve_id, scenario_id)
);

-- Mission-critical vulnerability view
CREATE VIEW mission_critical_vulnerabilities AS
WITH critical_paths AS (
  SELECT DISTINCT e.id as entity_id, e.name as entity_name
  FROM entities e
  JOIN relationships r ON e.id IN (r.source_id, r.target_id)
  JOIN control_loops cl ON r.control_loop_id = cl.id
  WHERE cl.controlled_process IN (
    SELECT jsonb_array_elements_text(mission_statement->'mission_dependencies') 
    FROM system_definition 
    WHERE id = 'system-001'
  )
),
ranked_vulns AS (
  SELECT 
    ev.*,
    e.name as entity_name,
    e.criticality as entity_criticality,
    cve.description,
    cve.cvss_severity,
    cve.known_exploited,
    cve.exploit_maturity,
    cp.entity_id IS NOT NULL as in_critical_path,
    ROW_NUMBER() OVER (
      PARTITION BY ev.entity_id 
      ORDER BY ev.contextual_risk_score DESC
    ) as risk_rank
  FROM entity_vulnerabilities ev
  JOIN entities e ON ev.entity_id = e.id
  JOIN cve_database cve ON ev.cve_id = cve.cve_id
  LEFT JOIN critical_paths cp ON e.id = cp.entity_id
  WHERE ev.status = 'open'
)
SELECT 
  entity_id,
  entity_name,
  entity_criticality,
  cve_id,
  cvss_severity,
  base_risk_score,
  contextual_risk_score,
  description,
  known_exploited,
  exploit_maturity,
  in_critical_path,
  CASE 
    WHEN in_critical_path AND contextual_risk_score > 70 THEN 'IMMEDIATE'
    WHEN contextual_risk_score > 80 THEN 'EMERGENCY'
    WHEN contextual_risk_score > 60 THEN 'CRITICAL'
    WHEN contextual_risk_score > 40 THEN 'HIGH'
    WHEN contextual_risk_score > 20 THEN 'MEDIUM'
    ELSE 'LOW'
  END as action_priority,
  compensating_controls,
  mitigation_deadline
FROM ranked_vulns
WHERE risk_rank <= 10  -- Top 10 risks per entity
ORDER BY 
  CASE WHEN in_critical_path THEN 0 ELSE 1 END,
  contextual_risk_score DESC;

-- Exploit prediction analysis
CREATE VIEW exploit_likelihood_prediction AS
WITH exploit_indicators AS (
  SELECT 
    cve.cve_id,
    cve.cvss_severity,
    cve.epss_score,
    cve.exploit_maturity,
    cve.published_date,
    
    -- Calculate days since publication
    EXTRACT(DAY FROM NOW() - cve.published_date) as days_since_published,
    
    -- Count affected entities
    COUNT(DISTINCT ev.entity_id) as affected_entity_count,
    COUNT(DISTINCT CASE WHEN e.exposure IN ('external', 'public') THEN e.id END) as external_entity_count,
    
    -- Calculate exploit probability
    CASE 
      WHEN cve.known_exploited THEN 1.0
      WHEN cve.in_the_wild THEN 0.9
      WHEN cve.exploit_maturity = 'high' THEN 0.8
      WHEN cve.exploit_maturity = 'functional' THEN 0.6
      WHEN cve.epss_score > 0.7 THEN cve.epss_score
      WHEN cve.epss_score > 0.3 THEN cve.epss_score * 1.2
      ELSE LEAST(cve.epss_score * 2, 0.3)
    END as exploit_probability,
    
    -- APT interest indicator
    CASE 
      WHEN array_length(cve.apt_association, 1) > 0 THEN TRUE
      ELSE FALSE
    END as apt_interest,
    
    -- Calculate potential business impact
    MAX(
      CASE e.criticality
        WHEN 'critical' THEN 1000000
        WHEN 'high' THEN 100000
        WHEN 'medium' THEN 10000
        ELSE 1000
      END * ev.data_sensitivity_multiplier
    ) as max_business_impact
    
  FROM cve_database cve
  LEFT JOIN entity_vulnerabilities ev ON cve.cve_id = ev.cve_id AND ev.status = 'open'
  LEFT JOIN entities e ON ev.entity_id = e.id
  GROUP BY cve.cve_id, cve.cvss_severity, cve.epss_score, cve.exploit_maturity, 
           cve.published_date, cve.known_exploited, cve.in_the_wild, cve.apt_association
)
SELECT 
  cve_id,
  cvss_severity,
  epss_score,
  exploit_probability,
  days_since_published,
  affected_entity_count,
  external_entity_count,
  
  -- Predict exploitation timeline
  CASE 
    WHEN exploit_probability > 0.8 THEN 'IMMINENT (< 7 days)'
    WHEN exploit_probability > 0.6 AND external_entity_count > 0 THEN 'VERY_LIKELY (< 30 days)'
    WHEN exploit_probability > 0.4 THEN 'LIKELY (< 90 days)'
    WHEN exploit_probability > 0.2 THEN 'POSSIBLE (< 180 days)'
    ELSE 'UNLIKELY (> 180 days)'
  END as exploitation_timeline,
  
  -- Risk category
  CASE 
    WHEN exploit_probability > 0.6 AND max_business_impact > 100000 THEN 'CRITICAL_PRIORITY'
    WHEN exploit_probability > 0.4 AND max_business_impact > 50000 THEN 'HIGH_PRIORITY'
    WHEN exploit_probability > 0.2 OR max_business_impact > 10000 THEN 'MEDIUM_PRIORITY'
    ELSE 'LOW_PRIORITY'
  END as remediation_priority,
  
  apt_interest,
  max_business_impact,
  
  -- Recommended actions
  CASE 
    WHEN exploit_probability > 0.8 THEN 'PATCH_IMMEDIATELY_OR_ISOLATE'
    WHEN exploit_probability > 0.6 THEN 'PATCH_WITHIN_72_HOURS'
    WHEN exploit_probability > 0.4 THEN 'PATCH_THIS_WEEK'
    WHEN exploit_probability > 0.2 THEN 'PATCH_THIS_MONTH'
    ELSE 'PATCH_QUARTERLY'
  END as recommended_action

FROM exploit_indicators
WHERE affected_entity_count > 0
ORDER BY exploit_probability DESC, max_business_impact DESC;

-- Function to import CVEs from external sources
CREATE OR REPLACE FUNCTION import_cve_batch(
  p_cves JSONB
) RETURNS TABLE (
  imported INT,
  updated INT,
  failed INT,
  errors JSONB
) AS $$
DECLARE
  v_imported INT := 0;
  v_updated INT := 0;
  v_failed INT := 0;
  v_errors JSONB := '[]'::JSONB;
  v_cve JSONB;
BEGIN
  FOR v_cve IN SELECT * FROM jsonb_array_elements(p_cves)
  LOOP
    BEGIN
      INSERT INTO cve_database (
        cve_id,
        published_date,
        last_modified,
        description,
        cvss_v3_score,
        cvss_severity,
        affected_products
      ) VALUES (
        v_cve->>'cve_id',
        (v_cve->>'published_date')::DATE,
        (v_cve->>'last_modified')::DATE,
        v_cve->>'description',
        (v_cve->>'cvss_v3_score')::FLOAT,
        v_cve->>'cvss_severity',
        v_cve->'affected_products'
      )
      ON CONFLICT (cve_id) DO UPDATE SET
        last_modified = EXCLUDED.last_modified,
        description = EXCLUDED.description,
        cvss_v3_score = EXCLUDED.cvss_v3_score,
        updated_at = NOW();
        
      IF FOUND THEN
        v_imported := v_imported + 1;
      ELSE
        v_updated := v_updated + 1;
      END IF;
      
    EXCEPTION WHEN OTHERS THEN
      v_failed := v_failed + 1;
      v_errors := v_errors || jsonb_build_object(
        'cve_id', v_cve->>'cve_id',
        'error', SQLERRM
      );
    END;
  END LOOP;
  
  RETURN QUERY SELECT v_imported, v_updated, v_failed, v_errors;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-map CVEs to entities based on technology
CREATE OR REPLACE FUNCTION auto_map_cves_to_entities() RETURNS TRIGGER AS $$
DECLARE
  v_entity RECORD;
  v_product JSONB;
BEGIN
  -- For each product in the CVE
  FOR v_product IN SELECT * FROM jsonb_array_elements(NEW.affected_products->'products')
  LOOP
    -- Find matching entities
    FOR v_entity IN 
      SELECT id, technology, version 
      FROM entities 
      WHERE technology ILIKE '%' || (v_product->>'product') || '%'
        OR properties->>'cpe' = v_product->>'cpe'
    LOOP
      -- Check version match
      IF v_entity.version IS NULL OR 
         v_entity.version = ANY(SELECT jsonb_array_elements_text(v_product->'versions')) THEN
        
        -- Create entity vulnerability mapping
        INSERT INTO entity_vulnerabilities (
          entity_id,
          cve_id,
          discovery_method,
          discovery_date,
          scanner_confidence
        ) VALUES (
          v_entity.id,
          NEW.cve_id,
          'auto_mapping',
          NOW(),
          0.7  -- 70% confidence for auto-mapping
        ) ON CONFLICT (entity_id, cve_id) DO NOTHING;
        
      END IF;
    END LOOP;
  END LOOP;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_map_cves
  AFTER INSERT OR UPDATE ON cve_database
  FOR EACH ROW
  EXECUTE FUNCTION auto_map_cves_to_entities();