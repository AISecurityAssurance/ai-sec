"""
JSON Schema definitions for Control Structure Analyst responses
"""

CONTROL_STRUCTURE_SCHEMA = {
    "type": "object",
    "properties": {
        "components": {
            "type": "object",
            "properties": {
                "controllers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "identifier": {"type": "string", "pattern": "^CTRL-[0-9]+$"},
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["human", "automated", "cyber-physical", "organizational"]},
                            "description": {"type": "string"},
                            "authority_level": {"type": "string", "enum": ["low", "medium", "high"]},
                            "hierarchical_level": {"type": "string", "enum": ["system", "subsystem", "component"]},
                            "controls": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["identifier", "name", "type", "description", "authority_level", "hierarchical_level", "controls"]
                    }
                },
                "controlled_processes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "identifier": {"type": "string", "pattern": "^PROC-[0-9]+$"},
                            "name": {"type": "string"},
                            "type": {"type": "string", "enum": ["physical", "computational", "informational", "financial"]},
                            "description": {"type": "string"},
                            "criticality": {"type": "string", "enum": ["low", "medium", "high"]},
                            "capabilities": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["identifier", "name", "type", "description", "criticality", "capabilities"]
                    }
                }
            },
            "required": ["controllers", "controlled_processes"]
        },
        "relationships": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "controller_id": {"type": "string"},
                    "process_id": {"type": "string"},
                    "relationship_type": {"type": "string", "enum": ["controls", "monitors", "configures", "coordinates"]},
                    "strength": {"type": "string", "enum": ["weak", "moderate", "strong"]}
                },
                "required": ["controller_id", "process_id", "relationship_type", "strength"]
            }
        },
        "hierarchy": {
            "type": "object",
            "properties": {
                "levels": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "level": {"type": "integer"},
                            "name": {"type": "string"},
                            "description": {"type": "string"},
                            "component_ids": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["level", "name", "description", "component_ids"]
                    }
                }
            },
            "required": ["levels"]
        },
        "summary": {"type": "string"}
    },
    "required": ["components", "relationships", "hierarchy", "summary"]
}