"""
JSON Schema definitions for Feedback Mechanism Agent responses
"""

FEEDBACK_MECHANISM_SCHEMA = {
    "type": "object",
    "properties": {
        "feedback_mechanisms": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "pattern": "^FB-[0-9]+$"},
                    "source_process_id": {"type": "string", "pattern": "^(PROC|CTRL|DUAL)-[0-9]+$"},
                    "target_controller_id": {"type": "string", "pattern": "^(CTRL|DUAL)-[0-9]+$"},
                    "feedback_name": {"type": "string"},
                    "information_type": {"type": "string", "enum": ["status", "measurement", "alert", "confirmation", "notification", "report"]},
                    "information_content": {"type": "string"},
                    "timing_characteristics": {
                        "type": "object",
                        "properties": {
                            "frequency": {"type": "string", "enum": ["continuous", "periodic", "event-driven", "on-demand"]},
                            "latency_requirement": {"type": "string"},
                            "staleness_tolerance": {"type": "string"}
                        },
                        "required": ["frequency", "latency_requirement", "staleness_tolerance"]
                    },
                    "reliability_requirements": {
                        "type": "object",
                        "properties": {
                            "availability": {"type": "string"},
                            "accuracy": {"type": "string", "enum": ["high", "medium", "low"]},
                            "integrity": {"type": "string"}
                        },
                        "required": ["availability", "accuracy", "integrity"]
                    },
                    "security_relevance": {"type": "string"}
                },
                "required": ["identifier", "source_process_id", "target_controller_id", 
                            "feedback_name", "information_type", "information_content",
                            "timing_characteristics", "reliability_requirements", "security_relevance"]
            }
        },
        "process_models": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "model_name": {"type": "string"},
                    "controller_id": {"type": "string", "pattern": "^(CTRL|DUAL)-[0-9]+$"},
                    "state_variables": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "update_sources": {
                        "type": "array",
                        "items": {"type": "string", "pattern": "^FB-[0-9]+$"}
                    },
                    "update_frequency": {"type": "string"},
                    "staleness_tolerance": {"type": "string"},
                    "assumptions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "potential_mismatches": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["model_name", "controller_id", "state_variables", 
                            "update_sources", "update_frequency", "staleness_tolerance",
                            "assumptions", "potential_mismatches"]
            }
        },
        "feedback_adequacy": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "control_action_id": {"type": "string", "pattern": "^CA-[0-9]+$"},
                    "has_execution_feedback": {"type": "boolean"},
                    "has_effect_feedback": {"type": "boolean"},
                    "unobservable_states": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "feedback_delay": {"type": "string"},
                    "adequacy_assessment": {"type": "string", "enum": ["sufficient", "partial", "insufficient"]},
                    "adequacy_score": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "required": ["control_action_id", "has_execution_feedback", "has_effect_feedback",
                            "unobservable_states", "feedback_delay", "adequacy_assessment", "adequacy_score"]
            }
        },
        "feedback_gaps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "impact": {"type": "string"},
                    "recommendation": {"type": "string"}
                },
                "required": ["description", "impact", "recommendation"]
            }
        },
        "feedback_coverage_metrics": {
            "type": "object",
            "properties": {
                "overall_coverage_score": {"type": "number", "minimum": 0, "maximum": 1},
                "critical_gaps_count": {"type": "integer", "minimum": 0},
                "coverage_by_component": {
                    "type": "object",
                    "additionalProperties": {"type": "number", "minimum": 0, "maximum": 1}
                },
                "coverage_by_type": {
                    "type": "object",
                    "properties": {
                        "execution_feedback": {"type": "number", "minimum": 0, "maximum": 1},
                        "effect_feedback": {"type": "number", "minimum": 0, "maximum": 1},
                        "state_monitoring": {"type": "number", "minimum": 0, "maximum": 1}
                    },
                    "required": ["execution_feedback", "effect_feedback", "state_monitoring"]
                }
            },
            "required": ["overall_coverage_score", "critical_gaps_count", "coverage_by_component", "coverage_by_type"]
        },
        "analysis_notes": {"type": "string"}
    },
    "required": ["feedback_mechanisms", "process_models", "feedback_adequacy", "feedback_gaps", "feedback_coverage_metrics", "analysis_notes"]
}