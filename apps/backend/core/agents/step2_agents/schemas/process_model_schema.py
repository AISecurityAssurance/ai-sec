"""
JSON Schema definitions for Process Model Analyst responses
"""

PROCESS_MODEL_SCHEMA = {
    "type": "object",
    "properties": {
        "models": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "pattern": "^PM-[0-9]+$"},
                    "controller_id": {"type": "string", "pattern": "^(CTRL|DUAL)-[0-9]+$"},
                    "process_id": {"type": "string", "pattern": "^(PROC|DUAL)-[0-9]+$"},
                    "state_variables": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string", "enum": ["boolean", "numeric", "enum", "composite"]},
                                "description": {"type": "string"},
                                "update_mechanism": {"type": "string"},
                                "potential_issues": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            },
                            "required": ["name", "type", "description", "update_mechanism", "potential_issues"]
                        }
                    },
                    "assumptions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "update_frequency": {"type": "string", "enum": ["continuous", "periodic", "event-driven"]},
                    "staleness_risk": {"type": "string", "enum": ["low", "medium", "high"]}
                },
                "required": ["identifier", "controller_id", "process_id", "state_variables", 
                            "assumptions", "update_frequency", "staleness_risk"]
            }
        },
        "algorithms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "pattern": "^ALG-[0-9]+$"},
                    "controller_id": {"type": "string", "pattern": "^(CTRL|DUAL)-[0-9]+$"},
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "constraints": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "enum": ["timing", "safety", "security", "resource"]},
                                "constraint": {"type": "string"},
                                "enforcement": {"type": "string"},
                                "violation_impact": {"type": "string"}
                            },
                            "required": ["type", "constraint", "enforcement", "violation_impact"]
                        }
                    },
                    "decision_logic": {"type": "string"},
                    "conflict_resolution": {"type": "string"}
                },
                "required": ["identifier", "controller_id", "name", "description", 
                            "constraints", "decision_logic", "conflict_resolution"]
            }
        },
        "insights": {
            "type": "object",
            "properties": {
                "model_coverage": {"type": "string"},
                "algorithm_sophistication": {"type": "string"},
                "information_dependencies": {"type": "string"},
                "timing_characteristics": {"type": "string"},
                "coordination_needs": {"type": "string"}
            },
            "required": ["model_coverage", "algorithm_sophistication", 
                        "information_dependencies", "timing_characteristics", "coordination_needs"]
        },
        "summary": {"type": "string"}
    },
    "required": ["models", "algorithms", "insights", "summary"]
}