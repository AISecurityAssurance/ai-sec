"""
JSON Schema definitions for Control Context Analyst responses
"""

CONTROL_CONTEXT_SCHEMA = {
    "type": "object",
    "properties": {
        "control_contexts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "control_action_id": {"type": "string", "pattern": "^CA-[0-9]+$"},
                    "execution_context": {
                        "type": "object",
                        "properties": {
                            "triggers": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "preconditions": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "environmental_factors": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "timing_requirements": {
                                "type": "object",
                                "properties": {
                                    "frequency": {"type": "string"},
                                    "response_time": {"type": "string"},
                                    "duration": {"type": "string"}
                                },
                                "required": ["frequency", "response_time", "duration"]
                            }
                        },
                        "required": ["triggers", "preconditions", "environmental_factors", "timing_requirements"]
                    },
                    "decision_logic": {
                        "type": "object",
                        "properties": {
                            "inputs_evaluated": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "decision_criteria": {"type": "string"},
                            "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                            "conflict_resolution": {"type": "string"}
                        },
                        "required": ["inputs_evaluated", "decision_criteria", "priority", "conflict_resolution"]
                    },
                    "process_model": {
                        "type": "object",
                        "properties": {
                            "state_beliefs": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "key_assumptions": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "update_sources": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "tracked_variables": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "staleness_handling": {"type": "string"},
                            "model_reality_gaps": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["state_beliefs", "key_assumptions", "update_sources",
                                    "tracked_variables", "staleness_handling", "model_reality_gaps"]
                    },
                    "controller_algorithm": {
                        "type": "object",
                        "properties": {
                            "decision_rules": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "input_prioritization": {"type": "string"},
                            "conflict_resolution": {"type": "string"},
                            "fallback_behavior": {"type": "string"},
                            "timing_logic": {"type": "string"}
                        },
                        "required": ["decision_rules", "input_prioritization", 
                                    "conflict_resolution", "fallback_behavior", "timing_logic"]
                    },
                    "applicable_modes": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["control_action_id", "execution_context", "decision_logic", "process_model", "controller_algorithm", "applicable_modes"]
            }
        },
        "operational_modes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "mode_name": {"type": "string"},
                    "description": {"type": "string"},
                    "entry_conditions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "exit_conditions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "active_controllers": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "available_actions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "mode_constraints": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["mode_name", "description", "entry_conditions", 
                            "exit_conditions", "active_controllers", "available_actions", "mode_constraints"]
            }
        },
        "mode_transitions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "from_mode": {"type": "string"},
                    "to_mode": {"type": "string"},
                    "transition_trigger": {"type": "string"},
                    "transition_actions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "transition_time": {"type": "string"}
                },
                "required": ["from_mode", "to_mode", "transition_trigger", "transition_actions", "transition_time"]
            }
        },
        "analysis_notes": {"type": "string"}
    },
    "required": ["control_contexts", "operational_modes", "mode_transitions", "analysis_notes"]
}