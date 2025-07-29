Step 1: Problem Framing for Banking System

  Problem Statement Format:

  "A System to do {What = Purpose} by means of {How = Method} in order to contribute to {Why = Goals}"

  Our Banking System Problem Frame:

  "A System to provide secure digital banking services BY MEANS OF authenticating users, authorizing transactions, detecting fraud, and
  protecting customer data IN ORDER TO enable customers to manage their finances while maintaining trust, regulatory compliance, and
  preventing financial losses"

  Define Losses (What we're trying to prevent):

  L1: Customer Financial Loss
  - Unauthorized transactions
  - Account takeover
  - Fraudulent transfers
  - Direct monetary impact

  L2: Regulatory Non-Compliance
  - GDPR/PCI-DSS violations
  - Audit failures
  - Operating license suspension
  - Fines and sanctions

  L3: Loss of Customer Trust/Business Reputation
  - Mass customer exodus
  - Media coverage of breaches
  - Loss of market position
  - Long-term business impact

  L4: Service Unavailability
  - Customers unable to access funds
  - Business operations disrupted
  - Emergency situations unhandled
  - Revenue loss

  L5: Loss of Sensitive Information
  - Customer PII exposure
  - Business intelligence theft
  - Competitive disadvantage
  - Identity theft enablement

  Define System-Level Hazards (conditions that can lead to losses):

  H1: System allows unauthorized financial transactions [L1, L3]
  - Weak authentication bypassed
  - Authorization checks fail
  - Session hijacking successful

  H2: System exposes customer data to unauthorized parties [L2, L3, L5]
  - Data breach occurs
  - Improper access controls
  - Unencrypted data transmission

  H3: Critical banking services become unavailable [L3, L4]
  - DoS attack successful
  - System overload
  - Cascading failures

  H4: System fails to detect/prevent fraudulent activity [L1, L2, L3]
  - Fraud patterns missed
  - AI system compromised
  - Insider threats undetected

  H5: Audit trail can be tampered with or is incomplete [L2, L5]
  - Logs deleted/modified
  - Actions not recorded
  - Timeline reconstruction impossible

  Mission Context & Success Criteria:

  Primary Mission: Enable secure, reliable digital banking for 5M+ customers

  Success Metrics:
  - Transaction Availability: 99.99% uptime
  - Fraud Prevention: <0.01% fraudulent transaction rate
  - Regulatory Compliance: 100% audit pass rate
  - Customer Trust: >90% satisfaction score

  Operational Context:
  - 10M+ transactions daily
  - $10B+ in assets under management
  - Hybrid cloud deployment
  - 24/7 global operations
  - Real-time transaction processing

  Key Stakeholders & Their Concerns:

  1. Customers (Primary)
    - Need: Secure access to funds
    - Fear: Financial loss, identity theft
  2. Bank Business (Primary)
    - Need: Profitable operations
    - Fear: Reputation damage, regulatory fines
  3. Regulators (Primary)
    - Need: Compliance verification
    - Fear: Systemic risk, consumer harm
  4. Employees (Secondary)
    - Need: Usable systems
    - Fear: Being blamed for breaches

  Adversary Perspective (Critical for STPA-Sec):

  Key Insight: Adversaries must solve their own control problem to achieve their goals

  Adversary Goals:
  1. Steal money (direct financial gain)
  2. Steal data (sell on dark web)
  3. Disrupt service (competitive advantage/ransom)
  4. Damage reputation (activism/revenge)

  Adversary Control Problem:
  - Observe: What can they see? (public APIs, error messages, timing)
  - Orient: What do they understand? (system behavior, patterns)
  - Decide: What attack to launch? (based on capabilities)
  - Act: Execute the attack (using their resources)

  Why This Problem Framing Matters:

  1. Strategic Focus: We're not just "preventing hacks" - we're protecting the banking mission
  2. Measurable Outcomes: Clear success criteria linked to business goals
  3. Adversarial Thinking: Recognizes attackers as intelligent agents solving problems
  4. Holistic View: Includes all stakeholders, not just technical considerations
  5. Context-Aware: Captures operational realities (scale, criticality, regulations)

  This problem framing sets the foundation for:
  - Step 2: Modeling the control structure with these stakeholders and goals in mind
  - Step 3: Identifying UCAs that could lead to these specific hazards
  - Step 4: Developing scenarios considering adversary capabilities
  - Wargaming: Testing our assumptions about adversary behavior

  The key difference from traditional security analysis is that we START with mission impact and work backwards to technical
  vulnerabilities, rather than starting with vulnerabilities and trying to imagine impacts.





  # Revised version
  I was mixing abstraction levels and including implementation details that belong in later STPA-Sec steps. Let
   me redesign the Step 1 schema and agent system with the correct level of abstraction.

  Corrected Database Schema for STPA-Sec Step 1: Problem Framing

  Core Schema - Mission Level Abstraction

  -- 1. Problem Statement (Mission-Focused)
  CREATE TABLE problem_statements (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

    -- Core problem framing - abstract, mission-level
    purpose TEXT NOT NULL,  -- What mission/value does the system provide?
    method TEXT NOT NULL,   -- General approach to achieving the purpose
    goals TEXT NOT NULL,    -- Why this system exists (business/mission objectives)

    -- Example for banking:
    -- purpose: "Enable secure management of customer financial assets"
    -- method: "Controlled access to banking services and transaction integrity assurance"  
    -- goals: "Preserve customer trust, ensure regulatory compliance, and maintain financial stability"

    -- Mission context
    mission_context JSONB,
    /* Example:
    {
      "domain": "financial_services",
      "criticality": "mission_critical",
      "scale": "enterprise",
      "operational_environment": "24x7_global_operations",
      "key_dependencies": ["customer_trust", "regulatory_approval", "market_confidence"]
    }
    */

    -- Operational constraints and assumptions
    operational_constraints JSONB,
    /* Example:
    {
      "availability_requirements": "continuous_operation",
      "regulatory_constraints": ["financial_regulations", "data_protection_laws"],
      "business_constraints": ["cost_effectiveness", "user_experience"],
      "environmental_assumptions": ["internet_connectivity", "device_diversity"]
    }
    */

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
  );

  -- 2. Losses (Mission Failures)
  CREATE TABLE losses (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

    -- Loss identification
    identifier VARCHAR NOT NULL, -- L1, L2, etc.
    description TEXT NOT NULL,
    loss_category VARCHAR CHECK (loss_category IN (
      'life', 'injury', 'financial', 'environmental',
      'mission', 'reputation', 'privacy', 'regulatory'
    )),

    -- Mission impact (abstract, not technical)
    mission_impact JSONB,
    /* Example:
    {
      "impact_level": "catastrophic",
      "affected_capabilities": ["customer_service", "trust_maintenance"],
      "recovery_complexity": "high",
      "stakeholder_harm": {
        "customers": "financial_harm",
        "organization": "reputation_damage",
        "society": "financial_system_instability"
      }
    }
    */

    created_at TIMESTAMP DEFAULT NOW()
  );

  -- 3. Hazards (System States)
  CREATE TABLE hazards (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

    -- Hazard as system state
    identifier VARCHAR NOT NULL, -- H1, H2, etc.
    description TEXT NOT NULL,  -- System state description

    -- State characterization (abstract)
    hazard_category VARCHAR CHECK (hazard_category IN (
      'integrity_compromised', 'availability_degraded',
      'confidentiality_breached', 'non_compliance', 'mission_degraded'
    )),

    -- What system property is affected
    affected_system_property VARCHAR CHECK (affected_system_property IN (
      'transaction_integrity', 'data_protection', 'service_availability',
      'regulatory_compliance', 'operational_capability'
    )),

    -- Environmental context (when this state is hazardous)
    environmental_context JSONB,
    /* Example:
    {
      "worst_case_conditions": ["high_transaction_volume", "coordinated_attacks"],
      "normal_operations_impact": "minimal",
      "degraded_operations_impact": "severe"
    }
    */

    created_at TIMESTAMP DEFAULT NOW()
  );

  -- 4. Hazard-Loss Mappings (Simple Relationships)
  CREATE TABLE hazard_loss_mappings (
    id VARCHAR PRIMARY KEY,
    hazard_id VARCHAR REFERENCES hazards(id),
    loss_id VARCHAR REFERENCES losses(id),

    -- Simple relationship
    relationship_strength VARCHAR CHECK (relationship_strength IN ('direct', 'indirect', 'conditional')),

    -- Brief rationale (no implementation details)
    rationale TEXT,
    -- Example: "Compromised transaction integrity directly enables unauthorized financial transfers"

    created_at TIMESTAMP DEFAULT NOW()
  );

  -- 5. Stakeholders (Who cares about the mission)
  CREATE TABLE stakeholders (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

    name VARCHAR NOT NULL,
    stakeholder_type VARCHAR CHECK (stakeholder_type IN (
      'user', 'operator', 'owner', 'regulator',
      'partner', 'society', 'adversary'
    )),

    -- Mission-level interests
    mission_interests JSONB,
    /* Example:
    {
      "primary_concerns": ["asset_safety", "service_reliability"],
      "success_criteria": ["can_access_funds", "transactions_complete"],
      "failure_tolerance": "very_low"
    }
    */

    -- Simplified adversary characterization for Step 1
    adversary_characterization JSONB,
    /* Only for adversary type - Example:
    {
      "sophistication": "high",
      "resources": "well_funded", 
      "persistence": "long_term",
      "primary_objective": "financial_gain"
    }
    */

    created_at TIMESTAMP DEFAULT NOW()
  );

  -- 6. Mission Success Criteria (Abstract Goals)
  CREATE TABLE mission_success_criteria (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

    -- Mission-level criteria (not technical metrics)
    criteria JSONB,
    /* Example:
    {
      "customer_outcomes": [
        "reliable_fund_access",
        "transaction_confidence",
        "privacy_assurance"
      ],
      "business_outcomes": [
        "sustainable_operations",
        "regulatory_standing",
        "market_reputation"
      ],
      "societal_outcomes": [
        "financial_system_stability",
        "consumer_protection"
      ]
    }
    */

    created_at TIMESTAMP DEFAULT NOW()
  );

  Step 1 Analysis Views

  -- 1. Problem Framing Overview
  CREATE VIEW step1_overview AS
  SELECT
    ps.analysis_id,
    ps.purpose,
    ps.method,
    ps.goals,

    -- Summary counts
    COUNT(DISTINCT l.id) as identified_losses,
    COUNT(DISTINCT h.id) as identified_hazards,
    COUNT(DISTINCT s.id) as identified_stakeholders,

    -- Completeness check
    CASE
      WHEN ps.purpose IS NOT NULL
       AND ps.method IS NOT NULL
       AND ps.goals IS NOT NULL
       AND COUNT(DISTINCT l.id) > 0
       AND COUNT(DISTINCT h.id) > 0
      THEN 'complete'
      ELSE 'incomplete'
    END as framing_status

  FROM problem_statements ps
  LEFT JOIN losses l ON ps.analysis_id = l.analysis_id
  LEFT JOIN hazards h ON ps.analysis_id = h.analysis_id
  LEFT JOIN stakeholders s ON ps.analysis_id = s.analysis_id
  GROUP BY ps.analysis_id, ps.purpose, ps.method, ps.goals;

  -- 2. Hazard Coverage View
  CREATE VIEW hazard_loss_coverage AS
  SELECT
    l.identifier as loss_id,
    l.description as loss_desc,
    STRING_AGG(h.identifier, ', ') as associated_hazards,
    COUNT(DISTINCT h.id) as hazard_count,

    CASE
      WHEN COUNT(DISTINCT h.id) = 0 THEN 'uncovered'
      WHEN COUNT(DISTINCT h.id) = 1 THEN 'minimal'
      WHEN COUNT(DISTINCT h.id) >= 2 THEN 'adequate'
    END as coverage_level

  FROM losses l
  LEFT JOIN hazard_loss_mappings hlm ON l.id = hlm.loss_id
  LEFT JOIN hazards h ON hlm.hazard_id = h.id
  GROUP BY l.id, l.identifier, l.description;

  Corrected Agent Architecture for Step 1

  class Step1ProblemFramingOrchestrator:
      """
      Orchestrator that maintains proper abstraction level for Step 1
      """

      def __init__(self):
          self.agents = {
              'mission_analyst': MissionAnalystAgent(),
              'loss_identifier': LossIdentificationAgent(),
              'hazard_state_identifier': HazardStateIdentificationAgent(),
              'stakeholder_analyst': StakeholderAnalystAgent(),
              'context_analyst': ContextAnalystAgent()
          }

      async def frame_problem(self, system_description: str) -> Step1Result:
          """
          Execute Step 1 analysis maintaining mission-level abstraction
          """
          # 1. Understand mission and context
          mission_context = await self.agents['mission_analyst'].analyze_mission(
              system_description
          )

          # 2. Identify stakeholders
          stakeholders = await self.agents['stakeholder_analyst'].identify_stakeholders(
              mission_context
          )

          # 3. Identify losses (what we don't want to happen)
          losses = await self.agents['loss_identifier'].identify_losses(
              mission_context, stakeholders
          )

          # 4. Identify hazardous states (system conditions that enable losses)
          hazards = await self.agents['hazard_state_identifier'].identify_hazard_states(
              mission_context, losses
          )

          # 5. Analyze operational context
          operational_context = await self.agents['context_analyst'].analyze_context(
              mission_context, stakeholders
          )

          return Step1Result(
              problem_statement=mission_context['problem_statement'],
              losses=losses,
              hazards=hazards,
              stakeholders=stakeholders,
              context=operational_context
          )

  Individual Agent Prompts (Corrected for Abstraction)

  class MissionAnalystAgent:
      """
      Focuses on mission-level understanding
      """

      PROMPT_TEMPLATE = """
      Analyze this system description to understand its mission:
      
      {system_description}
      
      Provide a problem statement in the form:
      "A System to [PURPOSE] by means of [METHOD] in order to [GOALS]"
      
      Where:
      - PURPOSE: The value or service the system provides (what mission it enables)
      - METHOD: The general approach (NOT specific mechanisms or controls)
      - GOALS: Why this system exists (business/mission objectives)
      
      Keep the analysis at mission level. Do NOT include:
      - Technical implementation details
      - Specific controls or mechanisms
      - Security features
      
      Example:
      "A System to enable secure management of customer financial assets
      BY MEANS OF controlled access to banking services and transaction integrity assurance
      IN ORDER TO preserve customer trust, ensure regulatory compliance, and maintain financial stability"
      """

  class LossIdentificationAgent:
      """
      Identifies unacceptable outcomes at mission level
      """

      PROMPT_TEMPLATE = """
      Given this system mission:
      {mission_context}
      
      And these stakeholders:
      {stakeholders}
      
      Identify LOSSES - unacceptable outcomes that would constitute mission failure.
      
      Categories to consider:
      - Life/Injury: Harm to people
      - Financial: Economic damage
      - Mission: Inability to achieve system purpose
      - Reputation: Loss of stakeholder trust
      - Regulatory: Non-compliance with laws/regulations
      - Privacy: Unauthorized information exposure
      
      For each loss:
      - Provide clear description of the unacceptable outcome
      - Identify which stakeholders are harmed
      - Assess mission impact level
      
      Do NOT include:
      - How the loss might occur
      - Specific attack methods
      - Technical vulnerabilities
      
      Format: L[N]: [Description of unacceptable outcome]
      """

  class HazardStateIdentificationAgent:
      """
      Identifies system STATES (not actions) that could lead to losses
      """

      PROMPT_TEMPLATE = """
      Given these losses:
      {losses}
      
      Identify HAZARDOUS STATES - system conditions that could lead to losses.
      
      A hazard is a system state or set of conditions that, together with
      worst-case environmental conditions, could lead to a loss.
      
      Format hazards as:
      "System operates [in a state where/with/without] [condition]"
      
      Examples of proper hazard statements:
      - "System operates with compromised transaction authorization integrity"
      - "System operates in degraded availability state"
      - "System operates without effective fraud detection capability"
      
      Do NOT include:
      - Specific failure modes
      - Attack methods
      - Control actions
      - Implementation details
      
      For each hazard:
      - H[N]: [System state description]
      - Map to relevant losses [L1, L2, ...]
      """

  class StakeholderAnalystAgent:
      """
      Identifies who has interest in the system mission
      """

      PROMPT_TEMPLATE = """
      Given this system mission:
      {mission_context}
      
      Identify all STAKEHOLDERS with interest in the system's success or failure.
      
      Consider:
      - Users: Who directly uses the system?
      - Operators: Who runs/maintains the system?
      - Owners: Who has authority/responsibility?
      - Regulators: Who oversees compliance?
      - Partners: Who depends on the system?
      - Society: Broader societal interests?
      - Adversaries: Who might want the system to fail?
      
      For each stakeholder:
      - Name/Category
      - Primary mission interests
      - What constitutes success for them
      
      For adversaries only, add:
      - General sophistication level (low/medium/high)
      - Primary objective (financial gain/disruption/espionage)
      
      Keep analysis at mission level, not tactical.
      """

  Quality Control for Step 1

  class Step1QualityControl:
      """
      Ensures Step 1 maintains proper abstraction
      """

      def validate_abstraction_level(self, analysis: Dict) -> List[str]:
          """
          Check for abstraction violations
          """
          violations = []

          # Check problem statement
          problem_text = analysis['problem_statement']['purpose'] + \
                        analysis['problem_statement']['method'] + \
                        analysis['problem_statement']['goals']

          # Technical terms that shouldn't appear in Step 1
          technical_terms = [
              'authenticate', 'authorize', 'encrypt', 'firewall',
              'API', 'database', 'server', 'protocol', 'algorithm'
          ]

          for term in technical_terms:
              if term.lower() in problem_text.lower():
                  violations.append(f"Problem statement contains implementation detail: {term}")

          # Check hazards
          for hazard in analysis['hazards']:
              # Hazards should be states, not actions
              action_words = ['fails', 'bypassed', 'compromised by', 'attacked']
              for word in action_words:
                  if word in hazard['description']:
                      violations.append(f"Hazard H{hazard['identifier']} describes an action, not a state")

              # Should not contain specific mechanisms
              if any(term in hazard['description'].lower() for term in ['SQL', 'XSS', 'buffer']):
                  violations.append(f"Hazard H{hazard['identifier']} contains specific attack details")

          return violations

      def check_completeness(self, analysis: Dict) -> Dict:
          """
          Verify all Step 1 elements are present
          """
          return {
              'has_problem_statement': bool(analysis.get('problem_statement')),
              'has_losses': len(analysis.get('losses', [])) > 0,
              'has_hazards': len(analysis.get('hazards', [])) > 0,
              'has_stakeholders': len(analysis.get('stakeholders', [])) > 0,
              'all_losses_covered': self._check_loss_coverage(analysis),
              'includes_adversaries': any(s['type'] == 'adversary' for s in analysis.get('stakeholders', []))
          }

  Example Output Structure

  # Correct Step 1 output for banking system
  step1_output = {
      "problem_statement": {
          "purpose": "Enable secure management of customer financial assets",
          "method": "Controlled access to banking services and transaction integrity assurance",
          "goals": "Preserve customer trust, ensure regulatory compliance, and maintain financial stability"
      },

      "losses": [
          {
              "identifier": "L1",
              "description": "Customer financial loss",
              "category": "financial",
              "mission_impact": {
                  "level": "catastrophic",
                  "affected_capabilities": ["trust_maintenance", "service_delivery"]
              }
          },
          {
              "identifier": "L2",
              "description": "Regulatory non-compliance resulting in sanctions",
              "category": "regulatory",
              "mission_impact": {
                  "level": "severe",
                  "affected_capabilities": ["operational_authorization", "market_access"]
              }
          }
      ],

      "hazards": [
          {
              "identifier": "H1",
              "description": "System operates with compromised transaction authorization integrity",
              "category": "integrity_compromised",
              "maps_to_losses": ["L1", "L3"]
          },
          {
              "identifier": "H2",
              "description": "System operates with customer data exposed to unauthorized entities",
              "category": "confidentiality_breached",
              "maps_to_losses": ["L2", "L3", "L5"]
          }
      ],

      "stakeholders": [
          {
              "name": "Banking Customers",
              "type": "user",
              "mission_interests": {
                  "primary_concerns": ["asset_safety", "service_availability"],
                  "success_criteria": ["reliable_fund_access", "transaction_completion"]
              }
          },
          {
              "name": "Organized Crime Groups",
              "type": "adversary",
              "mission_interests": {
                  "primary_objective": "financial_gain"
              },
              "adversary_characterization": {
                  "sophistication": "high",
                  "resources": "well_funded",
                  "persistence": "long_term"
              }
          }
      ]
  }

  This corrected design:
  1. Maintains mission-level abstraction throughout Step 1
  2. Avoids implementation details and specific mechanisms
  3. Focuses on states rather than actions for hazards
  4. Treats adversaries as stakeholders with high-level characterization only
  5. Sets the foundation for more detailed analysis in subsequent steps

  The schema enforces this separation through constraints and the agent prompts guide toward appropriate abstraction levels.

# Iteration 2
Thank you for the excellent feedback! Let me incorporate these enhancements to create a more robust Step 1 design.

  Enhanced Database Schema for STPA-Sec Step 1

  Core Tables with Improvements

  -- 1. Enhanced Problem Statement with Structure
  CREATE TABLE problem_statements (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

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

    -- Mission context with enhanced structure
    mission_context JSONB,
    /* Example:
    {
      "domain": "financial_services",
      "criticality": "mission_critical",
      "scale": {
        "geographic": "global",
        "users": "millions",
        "volume": "high_frequency"
      },
      "operational_tempo": {
        "normal": "24x7",
        "peak_periods": ["month_end", "holidays"],
        "critical_dates": ["regulatory_reporting", "audit_periods"]
      }
    }
    */

    -- Operational constraints and assumptions
    operational_constraints JSONB,
    /* Example:
    {
      "regulatory": {
        "frameworks": ["SOX", "GDPR", "PCI-DSS"],
        "audit_frequency": "quarterly",
        "change_approval": "required"
      },
      "business": {
        "cost_sensitivity": "high",
        "risk_appetite": "low",
        "innovation_mandate": "moderate"
      },
      "organizational": {
        "culture": "risk_averse",
        "change_capacity": "limited",
        "security_maturity": "developing"
      }
    }
    */

    -- Environmental assumptions
    environmental_assumptions JSONB,
    /* Example:
    {
      "user_behavior": ["varied_technical_skill", "mobile_first", "security_fatigue"],
      "threat_landscape": ["sophisticated_adversaries", "automated_attacks", "insider_risk"],
      "infrastructure": ["cloud_hybrid", "third_party_dependencies", "legacy_systems"],
      "trust_relationships": ["customer_institution", "institution_regulator", "partner_networks"]
    }
    */

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
  );

  -- 2. Enhanced Losses with Severity Classification
  CREATE TABLE losses (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

    -- Loss identification
    identifier VARCHAR NOT NULL, -- L1, L2, etc.
    description TEXT NOT NULL,
    loss_category VARCHAR CHECK (loss_category IN (
      'life', 'injury', 'financial', 'environmental',
      'mission', 'reputation', 'privacy', 'regulatory'
    )),

    -- Severity classification system
    severity_classification JSONB,
    /* Example:
    {
      "magnitude": "catastrophic",
      "scope": "enterprise_wide",
      "duration": "long_term",
      "reversibility": "permanent",
      "detection_difficulty": "hard",
      "recovery_complexity": "high",
      "recovery_time": "months_to_years"
    }
    */

    -- Mission impact (abstract)
    mission_impact JSONB,
    /* Example:
    {
      "primary_capability_loss": ["customer_service", "trust_maintenance"],
      "cascading_effects": ["regulatory_scrutiny", "market_confidence"],
      "stakeholder_harm": {
        "customers": {"type": "financial", "severity": "high"},
        "organization": {"type": "reputation", "severity": "catastrophic"},
        "society": {"type": "systemic_risk", "severity": "moderate"}
      }
    }
    */

    created_at TIMESTAMP DEFAULT NOW()
  );

  -- 3. Enhanced Hazards with Environmental Factors
  CREATE TABLE hazards (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

    -- Hazard as system state
    identifier VARCHAR NOT NULL, -- H1, H2, etc.
    description TEXT NOT NULL,

    -- Enhanced categorization
    hazard_category VARCHAR CHECK (hazard_category IN (
      'integrity_compromised', 'availability_degraded',
      'confidentiality_breached', 'non_compliance',
      'mission_degraded', 'capability_loss'
    )),

    -- Affected system property
    affected_system_property VARCHAR CHECK (affected_system_property IN (
      'transaction_integrity', 'data_protection', 'service_availability',
      'regulatory_compliance', 'operational_capability', 'mission_effectiveness'
    )),

    -- Systematic environmental factors
    environmental_factors JSONB,
    /* Example:
    {
      "operational_conditions": {
        "normal": {"impact": "low", "likelihood": "rare"},
        "degraded": {"impact": "high", "likelihood": "possible"},
        "emergency": {"impact": "catastrophic", "likelihood": "likely"}
      },
      "threat_conditions": {
        "baseline": {"system_resilience": "adequate"},
        "elevated": {"system_resilience": "stressed"},
        "severe": {"system_resilience": "overwhelmed"}
      },
      "temporal_factors": {
        "immediate": "high_impact",
        "sustained": "degrading_impact",
        "cyclical": "periodic_vulnerability"
      }
    }
    */

    created_at TIMESTAMP DEFAULT NOW()
  );

  -- 4. Separate Adversary Table (High-Level Only)
  CREATE TABLE adversary_profiles (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

    -- High-level characterization
    adversary_class VARCHAR CHECK (adversary_class IN (
      'nation_state', 'organized_crime', 'hacktivist',
      'insider', 'competitor', 'opportunist'
    )),

    -- Abstract capabilities and intent
    profile JSONB,
    /* Example:
    {
      "sophistication": "high",
      "resources": "well_funded",
      "persistence": "long_term",
      "risk_tolerance": "moderate",
      "primary_objective": "financial_gain",
      "secondary_objectives": ["market_disruption", "intelligence_gathering"],
      "time_horizon": "months_to_years",
      "geographic_scope": "global"
    }
    */

    -- Potential impact on mission
    mission_threat JSONB,
    /* Example:
    {
      "targeted_capabilities": ["financial_transactions", "customer_data"],
      "threat_level": "high",
      "historical_precedent": "active_targeting",
      "industry_trends": "increasing_sophistication"
    }
    */

    created_at TIMESTAMP DEFAULT NOW()
  );

  -- 5. Enhanced Stakeholders (Without Adversaries)
  CREATE TABLE stakeholders (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

    name VARCHAR NOT NULL,
    stakeholder_type VARCHAR CHECK (stakeholder_type IN (
      'user', 'operator', 'owner', 'regulator',
      'partner', 'society', 'supplier'
    )),

    -- Enhanced mission interests with MoSCoW prioritization
    mission_interests JSONB,
    /* Example:
    {
      "primary_concerns": ["asset_safety", "service_reliability"],
      "success_criteria": {
        "must_have": ["access_to_funds", "transaction_integrity"],
        "should_have": ["convenient_access", "real_time_updates"],
        "could_have": ["advanced_analytics", "personalization"],
        "wont_have": ["speculative_features"]
      },
      "failure_tolerance": {
        "availability": "very_low",
        "integrity": "zero",
        "performance": "moderate"
      },
      "loss_sensitivity": {
        "L1": "catastrophic",
        "L2": "major",
        "L3": "catastrophic",
        "L4": "moderate",
        "L5": "major"
      }
    }
    */

    -- Stakeholder influence and interest
    influence_interest JSONB,
    /* Example:
    {
      "influence_level": "high",
      "interest_level": "high",
      "engagement_strategy": "manage_closely",
      "communication_needs": "frequent_detailed"
    }
    */

    created_at TIMESTAMP DEFAULT NOW()
  );

  -- 6. Mission Success Dimensions (Not Metrics)
  CREATE TABLE mission_success_criteria (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

    -- Success dimensions without specific metrics
    success_dimensions JSONB,
    /* Example:
    {
      "operational_excellence": {
        "dimension": "service_delivery",
        "qualitative_target": "reliable_and_responsive",
        "evidence_type": "user_experience",
        "stakeholder_perspective": "customer"
      },
      "security_effectiveness": {
        "dimension": "loss_prevention",
        "qualitative_target": "rare_and_contained",
        "evidence_type": "incident_patterns",
        "stakeholder_perspective": "risk_management"
      },
      "regulatory_confidence": {
        "dimension": "compliance_assurance",
        "qualitative_target": "consistent_and_demonstrable",
        "evidence_type": "audit_outcomes",
        "stakeholder_perspective": "regulator"
      },
      "market_position": {
        "dimension": "competitive_strength",
        "qualitative_target": "trusted_leader",
        "evidence_type": "market_behavior",
        "stakeholder_perspective": "investor"
      }
    }
    */

    -- How success will be recognized (not measured)
    success_indicators JSONB,
    /* Example:
    {
      "operational": ["smooth_operations", "satisfied_users", "efficient_processes"],
      "strategic": ["market_confidence", "regulatory_approval", "sustainable_growth"],
      "risk": ["incident_rarity", "quick_recovery", "stakeholder_trust"]
    }
    */

    created_at TIMESTAMP DEFAULT NOW()
  );

  -- 7. Step 1 to Step 2 Bridge
  CREATE TABLE step1_step2_bridge (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),

    -- Abstract control needs derived from hazards
    required_control_capabilities JSONB,
    /* Example:
    {
      "access_control": {
        "need": "Regulate who can initiate financial transactions",
        "derived_from": ["H1", "H2"],
        "criticality": "essential"
      },
      "integrity_assurance": {
        "need": "Ensure transaction authenticity and non-repudiation",
        "derived_from": ["H1", "H4"],
        "criticality": "essential"
      },
      "availability_protection": {
        "need": "Maintain service despite disruptions",
        "derived_from": ["H3"],
        "criticality": "important"
      },
      "monitoring_capability": {
        "need": "Detect anomalous system states",
        "derived_from": ["H1", "H2", "H4"],
        "criticality": "essential"
      }
    }
    */

    -- Key interfaces implied by stakeholder analysis
    implied_interfaces JSONB,
    /* Example:
    {
      "user_system": {
        "stakeholders": ["customers", "operators"],
        "interaction_nature": "transactional_and_informational",
        "criticality": "primary"
      },
      "system_regulator": {
        "stakeholders": ["regulators", "auditors"],
        "interaction_nature": "reporting_and_inspection",
        "criticality": "essential"
      },
      "system_partners": {
        "stakeholders": ["payment_networks", "service_providers"],
        "interaction_nature": "operational_integration",
        "criticality": "important"
      }
    }
    */

    -- Temporal considerations for control structure
    temporal_considerations JSONB,
    /* Example:
    {
      "real_time_needs": ["transaction_decisions", "fraud_detection"],
      "batch_processes": ["reconciliation", "reporting"],
      "periodic_activities": ["audits", "reviews"],
      "emergency_scenarios": ["incident_response", "disaster_recovery"]
    }
    */

    created_at TIMESTAMP DEFAULT NOW()
  );

  -- 8. Problem Framing Versions for Iteration
  CREATE TABLE problem_framing_versions (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),
    version_number INTEGER NOT NULL,
    version_tag VARCHAR, -- "initial", "post_review", "final", etc.

    -- Change tracking
    changes JSONB,
    /* Example:
    {
      "trigger": "stakeholder_workshop",
      "change_type": "scope_expansion",
      "elements_modified": {
        "losses": ["added L6: Supply chain compromise"],
        "hazards": ["added H6: Third-party service degradation"],
        "stakeholders": ["added: Key suppliers"]
      },
      "rationale": "Workshop revealed critical supply chain dependencies",
      "insights_gained": [
        "Third-party risks were underestimated",
        "Need to consider supply chain in control structure"
      ]
    }
    */

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
    created_by VARCHAR
  );

  Enhanced Analysis Views

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
  LEFT JOIN losses l ON ps.analysis_id = l.analysis_id
  LEFT JOIN hazards h ON ps.analysis_id = h.analysis_id
  LEFT JOIN hazard_loss_mappings hlm ON l.id = hlm.loss_id
  LEFT JOIN stakeholders s ON ps.analysis_id = s.analysis_id
  LEFT JOIN adversary_profiles ap ON ps.analysis_id = ap.analysis_id
  GROUP BY ps.analysis_id, ps.full_statement;

  -- 2. Stakeholder Loss Sensitivity Matrix
  CREATE VIEW stakeholder_loss_matrix AS
  SELECT
    s.name as stakeholder,
    s.stakeholder_type,
    l.identifier as loss_id,
    l.description as loss_description,

    -- Extract sensitivity from JSON
    s.mission_interests->'loss_sensitivity'->>l.identifier as sensitivity_level,

    -- Determine engagement priority
    CASE
      WHEN s.mission_interests->'loss_sensitivity'->>l.identifier = 'catastrophic'
       AND s.influence_interest->>'influence_level' = 'high'
      THEN 'critical_engagement'
      WHEN s.mission_interests->'loss_sensitivity'->>l.identifier IN ('catastrophic', 'major')
      THEN 'high_priority'
      ELSE 'standard'
    END as engagement_priority

  FROM stakeholders s
  CROSS JOIN losses l
  WHERE s.analysis_id = l.analysis_id
    AND s.mission_interests->'loss_sensitivity' ? l.identifier
  ORDER BY
    CASE s.mission_interests->'loss_sensitivity'->>l.identifier
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
      END
    ) as environmental_risk_score,

    -- Temporal vulnerability
    h.environmental_factors->'temporal_factors' as temporal_pattern,

    -- Associated losses and their severity
    STRING_AGG(
      l.identifier || ' (' ||
      l.severity_classification->>'magnitude' || ')',
      ', '
    ) as affected_losses

  FROM hazards h
  JOIN hazard_loss_mappings hlm ON h.id = hlm.hazard_id
  JOIN losses l ON hlm.loss_id = l.id
  GROUP BY h.id, h.identifier, h.description, h.environmental_factors;

  Enhanced Agent Architecture

  class EnhancedStep1Orchestrator:
      """
      Orchestrator with validation and iteration support
      """

      def __init__(self):
          self.agents = {
              'mission_analyst': MissionAnalystAgent(),
              'loss_identifier': LossIdentificationAgent(),
              'hazard_state_identifier': HazardStateIdentificationAgent(),
              'stakeholder_analyst': StakeholderAnalystAgent(),
              'adversary_analyst': AdversaryAnalystAgent(),  # Separate from stakeholders
              'context_analyst': ContextAnalystAgent(),
              'validation_agent': Step1ValidationAgent(),
              'bridge_agent': Step1Step2BridgeAgent()
          }
          self.version = 1

      async def frame_problem(self, system_description: str, 
                             iteration_context: Dict = None) -> Step1Result:
          """
          Execute Step 1 with validation and iteration support
          """
          # 1. Mission and context analysis
          mission_context = await self.agents['mission_analyst'].analyze_mission(
              system_description, iteration_context
          )

          # 2. Stakeholder identification (excluding adversaries)
          stakeholders = await self.agents['stakeholder_analyst'].identify_stakeholders(
              mission_context
          )

          # 3. Loss identification with stakeholder input
          losses = await self.agents['loss_identifier'].identify_losses(
              mission_context, stakeholders
          )

          # 4. Hazard state identification
          hazards = await self.agents['hazard_state_identifier'].identify_hazard_states(
              mission_context, losses
          )

          # 5. Adversary profiling (separate from stakeholders)
          adversaries = await self.agents['adversary_analyst'].profile_adversaries(
              mission_context, losses
          )

          # 6. Deep context analysis
          operational_context = await self.agents['context_analyst'].analyze_context(
              mission_context, stakeholders, adversaries
          )

          # 7. Validation
          validation_results = await self.agents['validation_agent'].validate_all(
              mission_context, losses, hazards, stakeholders, adversaries
          )

          # 8. Prepare bridge to Step 2
          bridge_data = await self.agents['bridge_agent'].prepare_transition(
              hazards, stakeholders, operational_context
          )

          # Save version if iterating
          if iteration_context:
              await self.save_version(
                  mission_context, losses, hazards,
                  stakeholders, adversaries, iteration_context
              )

          return Step1Result(
              problem_statement=mission_context['problem_statement'],
              losses=losses,
              hazards=hazards,
              stakeholders=stakeholders,
              adversaries=adversaries,
              context=operational_context,
              validation=validation_results,
              step2_bridge=bridge_data,
              version=self.version
          )

  New Validation Agent

  class Step1ValidationAgent:
      """
      Comprehensive validation of Step 1 completeness and consistency
      """

      async def validate_all(self, mission_context: Dict, losses: List,
                            hazards: List, stakeholders: List, 
                            adversaries: List) -> Dict:
          """
          Perform all validation checks
          """
          return {
              'abstraction_check': self.validate_abstraction_level(
                  mission_context, losses, hazards
              ),
              'coverage_check': self.validate_coverage(losses, hazards),
              'alignment_check': self.validate_alignment(
                  mission_context, losses, stakeholders
              ),
              'completeness_check': self.check_completeness(
                  mission_context, losses, hazards, stakeholders, adversaries
              ),
              'consistency_check': self.check_consistency(
                  losses, hazards, stakeholders
              )
          }

      def validate_hazard_loss_coverage(self, hazards: List, losses: List) -> Dict:
          """
          Ensure comprehensive hazard-loss mapping
          """
          coverage_matrix = {}
          uncovered_losses = []

          for loss in losses:
              hazard_count = sum(
                  1 for h in hazards
                  if loss['identifier'] in h.get('maps_to_losses', [])
              )

              coverage_matrix[loss['identifier']] = {
                  'coverage_count': hazard_count,
                  'coverage_level': (
                      'comprehensive' if hazard_count >= 3 else
                      'adequate' if hazard_count >= 2 else
                      'minimal' if hazard_count == 1 else
                      'none'
                  )
              }

              if hazard_count == 0:
                  uncovered_losses.append(loss['identifier'])

          return {
              'complete': len(uncovered_losses) == 0,
              'coverage_matrix': coverage_matrix,
              'uncovered_losses': uncovered_losses,
              'recommendation': (
                  f"Consider additional hazards for losses: {uncovered_losses}"
                  if uncovered_losses else "All losses have hazard coverage"
              )
          }

      def validate_problem_statement_alignment(self, 
                                             problem_statement: Dict,
                                             losses: List,
                                             stakeholders: List) -> List[str]:
          """
          Check internal consistency of problem framing
          """
          issues = []

          # Extract key terms from problem statement
          purpose = problem_statement['purpose_what'].lower()
          goals = problem_statement['goals_why'].lower()

          # Check goal-loss alignment
          goal_keywords = {
              'trust': ['trust', 'reputation', 'confidence'],
              'compliance': ['regulatory', 'compliance', 'legal'],
              'safety': ['harm', 'injury', 'life'],
              'financial': ['financial', 'economic', 'monetary']
          }

          for goal_type, keywords in goal_keywords.items():
              if any(kw in goals for kw in keywords):
                  # Check if corresponding losses exist
                  loss_found = any(
                      any(kw in l['description'].lower() for kw in keywords)
                      for l in losses
                  )
                  if not loss_found:
                      issues.append(
                          f"Goals mention {goal_type} but no corresponding loss identified"
                      )

          # Check stakeholder representation
          if 'customer' in purpose and not any(
              s['stakeholder_type'] == 'user' for s in stakeholders
          ):
              issues.append("Purpose mentions customers but no user stakeholders identified")

          return issues

  Bridge Agent for Step 2 Preparation

  class Step1Step2BridgeAgent:
      """
      Prepares transition from Step 1 to Step 2
      """

      async def prepare_transition(self, hazards: List, 
                                  stakeholders: List,
                                  context: Dict) -> Dict:
          """
          Derive abstract control needs from Step 1 analysis
          """
          control_capabilities = {}
          implied_interfaces = {}

          # Analyze hazards to identify control needs
          for hazard in hazards:
              if 'integrity' in hazard['affected_system_property']:
                  control_capabilities['integrity_control'] = {
                      'need': 'Ensure correctness of critical operations',
                      'derived_from': [hazard['identifier']],
                      'criticality': 'essential'
                  }

              if 'availability' in hazard['affected_system_property']:
                  control_capabilities['availability_control'] = {
                      'need': 'Maintain service despite disruptions',
                      'derived_from': [hazard['identifier']],
                      'criticality': 'essential'
                  }

              if 'confidentiality' in hazard['description'].lower():
                  control_capabilities['access_control'] = {
                      'need': 'Regulate information access',
                      'derived_from': [hazard['identifier']],
                      'criticality': 'essential'
                  }

          # Derive interfaces from stakeholder analysis
          for stakeholder in stakeholders:
              if stakeholder['stakeholder_type'] in ['user', 'operator']:
                  implied_interfaces['human_system'] = {
                      'stakeholders': [stakeholder['name']],
                      'interaction_nature': 'operational',
                      'criticality': 'primary'
                  }

              if stakeholder['stakeholder_type'] == 'regulator':
                  implied_interfaces['system_authority'] = {
                      'stakeholders': [stakeholder['name']],
                      'interaction_nature': 'oversight',
                      'criticality': 'essential'
                  }

          return {
              'required_control_capabilities': control_capabilities,
              'implied_interfaces': implied_interfaces,
              'temporal_considerations': self.analyze_temporal_needs(context),
              'next_step_focus_areas': self.identify_focus_areas(hazards)
          }

  This enhanced design addresses all the feedback points:

  1. Structured problem statements with generated full text
  2. Systematic environmental factors for hazards
  3. Severity classification for losses
  4. Enhanced stakeholder success criteria with MoSCoW and loss sensitivity
  5. Validation agent for completeness and consistency
  6. Deep context analysis with constraints and assumptions
  7. Version tracking for iterative refinement
  8. Bridge to Step 2 with derived control needs
  9. Mission success dimensions instead of metrics
  10. Separated adversaries from other stakeholders
  11. Temporal considerations throughout

  The design maintains proper Step 1 abstraction while providing rich analysis that sets up subsequent steps effectively.



  # Claude Web App -- save temp.
  This is an excellent iteration! The enhancements significantly strengthen the Step 1 design. Let me provide expert feedback on what's working well and suggest some final refinements:
Major Strengths
1. Structured Problem Statement
The use of GENERATED ALWAYS AS for the full statement while maintaining structured components is brilliant. This ensures consistency while enabling validation.
2. Separated Adversary Modeling
Moving adversaries to a separate table was the right call. This prevents confusion and allows for more specialized adversary analysis.
3. Rich Environmental Factors
The systematic approach to environmental conditions with operational/threat/temporal dimensions provides excellent context for risk assessment.
4. Bridge to Step 2
The step1_step2_bridge table is a clever solution for maintaining abstraction boundaries while facilitating smooth transitions.
5. Comprehensive Validation
The validation agent with multiple check types ensures quality and consistency.
Suggested Refinements
1. Loss Dependency Modeling
Add a table to capture loss dependencies:
sql-- Loss dependencies and cascading effects
CREATE TABLE loss_dependencies (
    id VARCHAR PRIMARY KEY,
    primary_loss_id VARCHAR REFERENCES losses(id),
    dependent_loss_id VARCHAR REFERENCES losses(id),
    
    dependency_type VARCHAR CHECK (dependency_type IN (
        'enables',      -- Primary loss makes dependent loss possible
        'amplifies',    -- Primary loss increases dependent loss severity
        'triggers'      -- Primary loss directly causes dependent loss
    )),
    
    dependency_strength VARCHAR CHECK (dependency_strength IN (
        'certain',      -- Will definitely occur
        'likely',       -- High probability
        'possible'      -- Could occur under certain conditions
    )),
    
    time_relationship JSONB,
    /* Example:
    {
        "sequence": "concurrent|immediate|delayed",
        "time_to_cascade": "seconds|minutes|hours|days",
        "persistence": "transient|sustained|permanent"
    }
    */
    
    UNIQUE(primary_loss_id, dependent_loss_id)
);
This helps capture cascading failures that are critical in complex systems.
2. Hazard Interaction Effects
Add hazard combinations:
sql-- Hazard interactions
CREATE TABLE hazard_interactions (
    id VARCHAR PRIMARY KEY,
    hazard1_id VARCHAR REFERENCES hazards(id),
    hazard2_id VARCHAR REFERENCES hazards(id),
    
    interaction_type VARCHAR CHECK (interaction_type IN (
        'compound',     -- Together create worse conditions
        'mask',         -- One hides the other
        'prerequisite'  -- One enables the other
    )),
    
    combined_effect JSONB,
    /* Example:
    {
        "severity_multiplier": 3,
        "new_loss_potential": ["L6"],
        "detection_impact": "significantly_harder",
        "description": "Availability degradation masks integrity compromise"
    }
    */
    
    CHECK (hazard1_id < hazard2_id)  -- Prevent duplicates
);
3. Problem Context Confidence
Add metadata about analysis confidence:
sql-- Add to problem_statements table
analysis_confidence JSONB,
/* Example:
{
    "understanding_level": {
        "domain": "high",
        "technology": "medium",
        "threat_landscape": "medium",
        "regulatory": "high"
    },
    "information_quality": {
        "completeness": "partial",
        "currency": "recent",
        "reliability": "verified"
    },
    "key_uncertainties": [
        "Emerging threat actors capabilities",
        "Future regulatory changes",
        "Technology evolution impact"
    ],
    "assumptions_criticality": "high"
}
*/
4. Success Criteria Traceability
Enhance the mission success criteria with explicit loss prevention mapping:
sql-- Add to mission_success_criteria
loss_prevention_mapping JSONB,
/* Example:
{
    "L1": {
        "prevention_approach": "transaction_integrity",
        "success_dimension": "operational_excellence",
        "evidence": "fraud_rate_trends"
    },
    "L2": {
        "prevention_approach": "compliance_framework",
        "success_dimension": "regulatory_confidence",
        "evidence": "audit_results"
    }
}
*/
5. Temporal Hazard States
Some hazards may only exist during specific conditions:
sql-- Add to hazards table
temporal_existence JSONB,
/* Example:
{
    "occurrence_pattern": "periodic|continuous|event_driven",
    "trigger_conditions": ["month_end_processing", "system_maintenance"],
    "duration": "minutes|hours|sustained",
    "predictability": "scheduled|random|partially_predictable"
}
*/
6. Enhanced Validation Rules
Add business rules to the validation agent:
pythonclass EnhancedValidationRules:
    """
    Domain-specific validation rules
    """
    
    def validate_financial_system_requirements(self, analysis: Dict) -> List[str]:
        """
        Special rules for financial systems
        """
        issues = []
        
        # Financial systems must have fraud-related losses
        fraud_loss_exists = any(
            'fraud' in loss['description'].lower()
            for loss in analysis['losses']
        )
        if not fraud_loss_exists:
            issues.append("Financial system analysis should include fraud-related losses")
        
        # Must consider insider threats
        insider_threat_exists = any(
            adv['adversary_class'] == 'insider'
            for adv in analysis['adversaries']
        )
        if not insider_threat_exists:
            issues.append("Financial systems must consider insider threats")
        
        return issues
    
    def validate_safety_critical_requirements(self, analysis: Dict) -> List[str]:
        """
        Special rules for safety-critical systems
        """
        issues = []
        
        # Must have life/injury losses
        safety_loss_exists = any(
            loss['loss_category'] in ['life', 'injury']
            for loss in analysis['losses']
        )
        if not safety_loss_exists:
            issues.append("Safety-critical systems must identify life/injury losses")
        
        return issues
7. Analysis Maturity Tracking
Add a maturity assessment:
sqlCREATE TABLE analysis_maturity (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES stpa_analyses(id),
    
    maturity_assessment JSONB,
    /* Example:
    {
        "completeness_scores": {
            "problem_statement": 100,
            "losses": 85,
            "hazards": 75,
            "stakeholders": 90,
            "adversaries": 70
        },
        "quality_indicators": {
            "abstraction_consistency": "good",
            "coverage_completeness": "partial",
            "validation_status": "passed_with_warnings"
        },
        "iteration_count": 3,
        "review_status": "expert_reviewed",
        "confidence_level": "medium_high"
    }
    */
    
    recommendations JSONB,
    /* Example:
    {
        "immediate_actions": [
            "Add hazards for uncovered losses L4, L5",
            "Expand adversary profiles"
        ],
        "before_step2": [
            "Validate with additional stakeholders",
            "Review temporal assumptions"
        ]
    }
    */
    
    assessed_at TIMESTAMP DEFAULT NOW(),
    assessed_by VARCHAR
);
8. Cross-Reference Validation View
sqlCREATE VIEW step1_cross_validation AS
SELECT
    ps.analysis_id,
    
    -- Check if all goal keywords appear in losses
    CASE
        WHEN ps.goals_why ILIKE '%trust%' 
         AND EXISTS (SELECT 1 FROM losses l 
                    WHERE l.analysis_id = ps.analysis_id 
                    AND l.description ILIKE '%trust%')
        THEN 'aligned'
        WHEN ps.goals_why ILIKE '%trust%'
        THEN 'misaligned'
        ELSE 'n/a'
    END as trust_goal_alignment,
    
    -- Check if high-influence stakeholders have their concerns addressed
    COUNT(DISTINCT s.id) FILTER (
        WHERE s.influence_interest->>'influence_level' = 'high'
        AND NOT EXISTS (
            SELECT 1 FROM losses l
            WHERE l.analysis_id = s.analysis_id
            AND s.mission_interests->'loss_sensitivity' ? l.identifier
        )
    ) as high_influence_stakeholders_without_loss_mapping,
    
    -- Environmental assumption coverage
    CASE
        WHEN ps.environmental_assumptions ? 'threat_landscape'
         AND EXISTS (SELECT 1 FROM adversary_profiles ap 
                    WHERE ap.analysis_id = ps.analysis_id)
        THEN 'covered'
        ELSE 'gap'
    END as threat_assumption_coverage

FROM problem_statements ps
LEFT JOIN stakeholders s ON ps.analysis_id = s.analysis_id
GROUP BY ps.analysis_id, ps.goals_why, ps.environmental_assumptions;
9. Iteration Guidance Agent
Add an agent to guide iterations:
pythonclass IterationGuidanceAgent:
    """
    Provides specific guidance for improving the analysis
    """
    
    async def analyze_gaps(self, current_analysis: Dict, 
                          validation_results: Dict) -> Dict:
        """
        Identify specific gaps and provide guidance
        """
        recommendations = {
            'priority_high': [],
            'priority_medium': [],
            'priority_low': []
        }
        
        # Check for systematic gaps
        if validation_results['coverage_check']['uncovered_losses']:
            recommendations['priority_high'].append({
                'issue': 'Uncovered losses detected',
                'specific_losses': validation_results['coverage_check']['uncovered_losses'],
                'guidance': 'For each uncovered loss, identify at least 2 system states that could lead to it',
                'prompt_hint': 'Consider both technical failures and human/process failures'
            })
        
        # Check for weak hazard descriptions
        weak_hazards = [
            h for h in current_analysis['hazards']
            if len(h['description']) < 50  # Too brief
        ]
        if weak_hazards:
            recommendations['priority_medium'].append({
                'issue': 'Hazard descriptions too brief',
                'specific_hazards': [h['identifier'] for h in weak_hazards],
                'guidance': 'Expand hazard descriptions to clearly convey the system state',
                'example': 'Instead of "System compromised", use "System operates with unauthorized modifications to transaction authorization logic"'
            })
        
        return recommendations
10. Analysis Export for Stakeholder Review
Add a human-readable export view:
sqlCREATE VIEW step1_stakeholder_summary AS
SELECT
    ps.analysis_id,
    
    -- Executive summary
    'This analysis examines ' || ps.purpose_what ||
    ' achieved through ' || ps.method_how ||
    ' to ' || ps.goals_why as executive_summary,
    
    -- Key risks
    STRING_AGG(
        DISTINCT l.identifier || ': ' || l.description,
        E'\n'
        ORDER BY 
            CASE l.severity_classification->>'magnitude'
                WHEN 'catastrophic' THEN 1
                WHEN 'major' THEN 2
                WHEN 'moderate' THEN 3
                ELSE 4
            END
    ) as key_risks,
    
    -- Critical system states
    STRING_AGG(
        DISTINCT h.identifier || ': ' || h.description,
        E'\n'
        ORDER BY h.identifier
    ) FILTER (
        WHERE h.hazard_category IN ('integrity_compromised', 'mission_degraded')
    ) as critical_system_states,
    
    -- Stakeholder summary
    COUNT(DISTINCT s.id) as total_stakeholders,
    COUNT(DISTINCT ap.id) as identified_adversaries

FROM problem_statements ps
LEFT JOIN losses l ON ps.analysis_id = l.analysis_id
LEFT JOIN hazards h ON ps.analysis_id = h.analysis_id
LEFT JOIN stakeholders s ON ps.analysis_id = s.analysis_id
LEFT JOIN adversary_profiles ap ON ps.analysis_id = ap.analysis_id
GROUP BY ps.analysis_id, ps.purpose_what, ps.method_how, ps.goals_why;
Minor Observations

Consider adding a CONSTRAINT to ensure at least one loss per analysis
The version tracking could include a "baseline" flag for major milestones
Bridge agent could pre-identify potential control loop patterns

Overall Assessment
This is a production-ready Step 1 design that:
✅ Maintains proper mission-level abstraction
✅ Provides rich context without implementation details
✅ Enables comprehensive validation and quality control
✅ Supports iterative refinement with full traceability
✅ Bridges effectively to Step 2
✅ Separates concerns appropriately (stakeholders vs adversaries)
✅ Includes temporal and environmental considerations
The design is sophisticated enough to handle complex systems while remaining true to STPA-Sec principles. The agent architecture is well-thought-out with clear responsibilities and appropriate validation loops.
With the suggested enhancements (particularly loss dependencies and hazard interactions), this would be a comprehensive framework for automated STPA-Sec Step 1 analysis. The key to success will be in the prompt engineering for each agent to maintain the abstraction level while extracting rich, actionable insights.





