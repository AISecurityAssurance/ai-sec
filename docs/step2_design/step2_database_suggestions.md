~-- STPA-Sec Step 2: Control Structure Schema
-- Designed with formal verification and state machine analysis in mind

-- Core Control Structure Tables

CREATE TABLE step2_analyses (
    id VARCHAR PRIMARY KEY,
    step1_analysis_id VARCHAR REFERENCES step1_analyses(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    description TEXT,
    abstraction_level VARCHAR CHECK (abstraction_level IN ('service', 'class', 'method')) DEFAULT 'service',
    codebase_path VARCHAR, -- Optional: path to analyzed codebase
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- System Components (Controllers and Controlled Processes)
CREATE TABLE system_components (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL, -- C-1, C-2, etc.
    name VARCHAR NOT NULL,
    component_type VARCHAR CHECK (component_type IN ('controller', 'controlled_process', 'hybrid')) NOT NULL,
    
    -- Code mapping (for codebase integration)
    code_location JSONB, 
    /* Example:
    {
        "file_path": "src/auth/AuthService.java",
        "class_name": "AuthService", 
        "interfaces": ["IAuthController"],
        "dependencies": ["UserRepository", "TokenService"]
    }
    */
    
    -- Component characteristics
    authority_level VARCHAR CHECK (authority_level IN ('none', 'local', 'system', 'administrative', 'root')),
    trust_level VARCHAR CHECK (trust_level IN ('untrusted', 'partially_trusted', 'trusted', 'critical')),
    
    -- State machine readiness
    has_state_machine BOOLEAN DEFAULT FALSE,
    state_machine_type VARCHAR CHECK (state_machine_type IN ('simple', 'hierarchical', 'concurrent', 'secure')),
    
    -- Security properties
    authentication_required BOOLEAN DEFAULT FALSE,
    authorization_model VARCHAR, -- RBAC, ABAC, etc.
    
    properties JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Control Actions (CA)
CREATE TABLE control_actions (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL, -- CA-1, CA-2, etc.
    name VARCHAR NOT NULL,
    description TEXT,
    
    -- Relationship
    controller_id VARCHAR REFERENCES system_components(id) ON DELETE CASCADE,
    controlled_process_id VARCHAR REFERENCES system_components(id) ON DELETE CASCADE,
    
    -- Action characteristics
    action_type VARCHAR CHECK (action_type IN ('command', 'query', 'configuration', 'authentication', 'authorization')),
    timing_type VARCHAR CHECK (timing_type IN ('synchronous', 'asynchronous', 'periodic', 'event_driven')),
    
    -- State machine integration
    triggers_state_transition BOOLEAN DEFAULT FALSE,
    source_state VARCHAR,
    target_state VARCHAR,
    transition_conditions JSONB,
    
    -- Security requirements
    requires_authentication BOOLEAN DEFAULT FALSE,
    requires_authorization BOOLEAN DEFAULT FALSE,
    authorization_policy TEXT,
    
    -- Code mapping
    implementation_details JSONB,
    /* Example:
    {
        "method_signature": "authenticate(String username, String password)",
        "api_endpoint": "POST /auth/login",
        "preconditions": ["user_exists", "password_valid"],
        "postconditions": ["session_created", "user_authenticated"]
    }
    */
    
    -- Timing and constraints
    timing_constraints JSONB,
    /* Example:
    {
        "max_response_time": "500ms",
        "timeout": "30s",
        "retry_policy": "exponential_backoff",
        "idempotent": true
    }
    */
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Feedback Mechanisms (FB)
CREATE TABLE feedback_mechanisms (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL, -- FB-1, FB-2, etc.
    name VARCHAR NOT NULL,
    description TEXT,
    
    -- Relationship
    source_process_id VARCHAR REFERENCES system_components(id) ON DELETE CASCADE,
    target_controller_id VARCHAR REFERENCES system_components(id) ON DELETE CASCADE,
    
    -- Information characteristics
    information_type VARCHAR CHECK (information_type IN ('status', 'data', 'error', 'metric', 'event')),
    content_description TEXT,
    
    -- State machine integration
    conveys_state_information BOOLEAN DEFAULT FALSE,
    state_variables JSONB, -- What state information is conveyed
    
    -- Security properties
    requires_integrity_protection BOOLEAN DEFAULT FALSE,
    requires_confidentiality BOOLEAN DEFAULT FALSE,
    authentication_mechanism VARCHAR,
    
    -- Timing properties
    delivery_guarantees VARCHAR CHECK (delivery_guarantees IN ('at_most_once', 'at_least_once', 'exactly_once')),
    timing_requirements JSONB,
    
    -- Code mapping
    implementation_details JSONB,
    /* Example:
    {
        "mechanism": "callback",
        "protocol": "HTTP",
        "format": "JSON",
        "endpoint": "POST /webhooks/auth-status"
    }
    */
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Process Models (Controller State and Logic)
CREATE TABLE process_models (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    controller_id VARCHAR REFERENCES system_components(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    
    -- Controller's understanding of system
    assumed_state JSONB,
    /* Example:
    {
        "user_state": "unauthenticated",
        "session_state": "none",
        "system_load": "normal",
        "security_posture": "nominal"
    }
    */
    
    -- Decision logic
    decision_algorithm TEXT,
    decision_factors JSONB, -- What factors influence decisions
    
    -- State management
    state_update_sources JSONB, -- How the controller learns about state changes
    state_staleness_tolerance VARCHAR,
    
    -- Formal verification readiness
    formal_specification TEXT, -- Space for formal logic specifications
    invariants JSONB, -- System invariants the controller maintains
    
    -- Security assumptions
    trust_assumptions JSONB,
    threat_model JSONB,
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Trust Boundaries (Security Perimeters)
CREATE TABLE trust_boundaries (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    identifier VARCHAR NOT NULL, -- TB-1, TB-2, etc.
    name VARCHAR NOT NULL,
    description TEXT,
    
    -- Boundary definition
    side_a_component_id VARCHAR REFERENCES system_components(id),
    side_b_component_id VARCHAR REFERENCES system_components(id),
    boundary_type VARCHAR CHECK (boundary_type IN ('network', 'process', 'privilege', 'data', 'trust')),
    
    -- Security mechanisms
    authentication_mechanism VARCHAR,
    authorization_mechanism VARCHAR,
    encryption_required BOOLEAN DEFAULT FALSE,
    integrity_protection BOOLEAN DEFAULT FALSE,
    
    -- State machine security
    enforces_secure_transitions BOOLEAN DEFAULT FALSE,
    transition_verification_method VARCHAR,
    
    -- Validation properties
    complete_mediation BOOLEAN DEFAULT FALSE, -- Every access checked
    fail_secure BOOLEAN DEFAULT FALSE, -- Fail to secure state
    
    properties JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- State Machine Definitions (For formal verification readiness)
CREATE TABLE state_machines (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    component_id VARCHAR REFERENCES system_components(id) ON DELETE CASCADE,
    name VARCHAR NOT NULL,
    
    -- State machine properties
    machine_type VARCHAR CHECK (machine_type IN ('deterministic', 'nondeterministic', 'secure')),
    
    -- States and transitions
    states JSONB, -- Array of state definitions
    /* Example:
    [
        {"name": "unauthenticated", "secure": false, "properties": {"access_level": "none"}},
        {"name": "authenticated", "secure": true, "properties": {"access_level": "user"}},
        {"name": "privileged", "secure": true, "properties": {"access_level": "admin"}}
    ]
    */
    
    transitions JSONB, -- Array of transition definitions
    /* Example:
    [
        {
            "from": "unauthenticated",
            "to": "authenticated", 
            "trigger": "successful_login",
            "guards": ["valid_credentials", "account_not_locked"],
            "actions": ["create_session", "log_access"]
        }
    ]
    */
    
    -- Formal verification elements
    initial_state VARCHAR NOT NULL,
    accepting_states JSONB, -- Final/accepting states
    invariants JSONB, -- Properties that must always hold
    security_properties JSONB, -- Security-specific invariants
    
    -- Implementation mapping
    implementation_mapping JSONB,
    /* Example:
    {
        "framework": "Spring State Machine",
        "config_file": "auth-state-machine.xml",
        "implementation_class": "AuthStateMachine"
    }
    */
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Control Action to State Transition Mapping
CREATE TABLE control_action_transitions (
    control_action_id VARCHAR REFERENCES control_actions(id) ON DELETE CASCADE,
    state_machine_id VARCHAR REFERENCES state_machines(id) ON DELETE CASCADE,
    transition_name VARCHAR NOT NULL,
    verification_requirements JSONB,
    /* Example:
    {
        "authentication_required": true,
        "authorization_policy": "user_can_transition",
        "additional_checks": ["rate_limit", "fraud_detection"]
    }
    */
    PRIMARY KEY (control_action_id, state_machine_id, transition_name)
);

-- Codebase Analysis Results (For code-aware analysis)
CREATE TABLE codebase_analysis (
    id VARCHAR PRIMARY KEY,
    analysis_id VARCHAR REFERENCES step2_analyses(id) ON DELETE CASCADE,
    
    -- Analysis metadata
    codebase_path VARCHAR NOT NULL,
    analysis_timestamp TIMESTAMP DEFAULT NOW(),
    analysis_tool VARCHAR, -- Name of tool used for analysis
    
    -- Extracted components
    discovered_components JSONB,
    /* Example:
    {
        "services": ["AuthService", "PaymentService", "UserService"],
        "controllers": ["AuthController", "PaymentController"],
        "entities": ["User", "Transaction", "Account"],
        "interfaces": ["IAuthenticator", "IPaymentProcessor"]
    }
    */
    
    -- Discovered relationships
    discovered_relationships JSONB,
    /* Example:
    [
        {"from": "AuthController", "to": "AuthService", "type": "uses"},
        {"from": "AuthService", "to": "UserRepository", "type": "depends_on"}
    ]
    */
    
    -- Security annotations found
    security_annotations JSONB,
    /* Example:
    {
        "authentication_annotations": ["@Authenticated", "@RequiresAuth"],
        "authorization_annotations": ["@Authorized", "@RolesAllowed"],
        "state_machine_annotations": ["@StateMachine", "@State"]
    }
    */
    
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_control_actions_controller ON control_actions(controller_id);
CREATE INDEX idx_control_actions_controlled_process ON control_actions(controlled_process_id);
CREATE INDEX idx_feedback_mechanisms_source ON feedback_mechanisms(source_process_id);
CREATE INDEX idx_feedback_mechanisms_target ON feedback_mechanisms(target_controller_id);
CREATE INDEX idx_process_models_controller ON process_models(controller_id);
CREATE INDEX idx_state_machines_component ON state_machines(component_id);

-- Views for analysis
CREATE VIEW control_structure_summary AS
SELECT 
    sa.id as analysis_id,
    sa.name as analysis_name,
    COUNT(DISTINCT sc.id) as total_components,
    COUNT(DISTINCT CASE WHEN sc.component_type = 'controller' THEN sc.id END) as controllers,
    COUNT(DISTINCT CASE WHEN sc.component_type = 'controlled_process' THEN sc.id END) as controlled_processes,
    COUNT(DISTINCT ca.id) as control_actions,
    COUNT(DISTINCT fb.id) as feedback_mechanisms,
    COUNT(DISTINCT tb.id) as trust_boundaries,
    COUNT(DISTINCT sm.id) as state_machines
FROM step2_analyses sa
LEFT JOIN system_components sc ON sa.id = sc.analysis_id
LEFT JOIN control_actions ca ON sa.id = ca.analysis_id  
LEFT JOIN feedback_mechanisms fb ON sa.id = fb.analysis_id
LEFT JOIN trust_boundaries tb ON sa.id = tb.analysis_id
LEFT JOIN state_machines sm ON sa.id = sm.analysis_id
GROUP BY sa.id, sa.name;~

