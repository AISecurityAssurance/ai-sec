"""
JSON Schema definitions for Trust Boundary Agent responses
"""

TRUST_BOUNDARY_SCHEMA = {
    "type": "object",
    "properties": {
        "trust_boundaries": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "identifier": {"type": "string", "pattern": "^TB-[0-9]+$"},
                    "boundary_name": {"type": "string"},
                    "boundary_type": {"type": "string", "enum": ["network", "authentication", "authorization", "data_classification", "organizational", "physical"]},
                    "component_a_id": {"type": "string", "pattern": "^(CTRL|PROC|DUAL)-[0-9]+$"},
                    "component_b_id": {"type": "string", "pattern": "^(CTRL|PROC|DUAL)-[0-9]+$"},
                    "trust_direction": {"type": "string", "enum": ["bidirectional", "a_trusts_b", "b_trusts_a", "none"]},
                    "trust_rationale": {"type": "string"},
                    "authentication_method": {"type": "string"},
                    "authorization_method": {"type": "string"},
                    "data_protection": {
                        "type": "object",
                        "properties": {
                            "encryption": {"type": "string"},
                            "integrity": {"type": "string"},
                            "confidentiality": {"type": "string"}
                        },
                        "required": ["encryption", "integrity", "confidentiality"]
                    },
                    "security_controls": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "trust_assumptions": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "verification_methods": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "required": ["identifier", "boundary_name", "boundary_type", 
                            "component_a_id", "component_b_id", "trust_direction",
                            "trust_rationale", "authentication_method", "authorization_method",
                            "data_protection", "security_controls", "trust_assumptions", "verification_methods"]
            }
        },
        "trust_mechanisms": {
            "type": "object",
            "properties": {
                "authentication_protocols": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "authorization_schemes": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "data_protection": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "trust_establishment": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "trust_maintenance": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["authentication_protocols", "authorization_schemes", 
                        "data_protection", "trust_establishment", "trust_maintenance"]
        },
        "analysis_notes": {"type": "string"}
    },
    "required": ["trust_boundaries", "trust_mechanisms", "analysis_notes"]
}