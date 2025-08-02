"""
JSON Schema definitions for Control Action Mapping Agent responses
"""

CONTROL_ACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "control_actions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "pattern": "^CA-[0-9]+$"},
                    "controller_id": {"type": "string", "pattern": "^(CTRL|DUAL)-[0-9]+$"},
                    "controlled_process_id": {"type": "string", "pattern": "^(PROC|DUAL)-[0-9]+$"},
                    "action_name": {"type": "string"},
                    "action_description": {"type": "string"},
                    "action_type": {"type": "string", "enum": ["command", "configuration", "permission", "monitoring"]},
                    "authority_level": {"type": "string", "enum": ["mandatory", "optional", "emergency"]},
                    "timing_requirements": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["periodic", "on-demand", "event-driven", "continuous"]},
                            "details": {"type": "string"}
                        },
                        "required": ["type", "details"]
                    },
                    "security_relevance": {"type": "string"}
                },
                "required": ["identifier", "controller_id", "controlled_process_id", 
                            "action_name", "action_description", "action_type", 
                            "authority_level", "timing_requirements", "security_relevance"]
            }
        },
        "control_contexts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "control_action_id": {"type": "string", "pattern": "^CA-[0-9]+$"},
                    "valid_states": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "prohibited_states": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "preconditions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "postconditions": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["control_action_id", "valid_states", "prohibited_states", 
                            "preconditions", "postconditions"]
            }
        },
        "completeness_check": {
            "type": "object",
            "properties": {
                "controllers_without_actions": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "processes_without_control": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "orphan_components": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "coverage_assessment": {"type": "string"}
            },
            "required": ["controllers_without_actions", "processes_without_control", 
                        "orphan_components", "coverage_assessment"]
        },
        "analysis_notes": {"type": "string"}
    },
    "required": ["control_actions", "control_contexts", "completeness_check", "analysis_notes"]
}