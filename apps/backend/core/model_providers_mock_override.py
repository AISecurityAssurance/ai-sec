"""
Temporary override for MockModelClient to return proper JSON responses
Place this at the end of core/model_providers.py in the Docker container
"""

# Override the MockModelClient class
import json
from typing import List, Dict, Optional

class MockModelClientFixed(BaseModelClient):
    """Mock client for testing without real LLM calls"""
    
    async def generate(self, messages: List[Dict[str, str]], 
                      temperature: float = 0.7,
                      max_tokens: Optional[int] = None) -> ModelResponse:
        """Generate mock response that always returns valid JSON"""
        
        # Always return a comprehensive mock response
        response_data = {
            "components": {
                "controllers": [
                    {
                        "identifier": "CTRL-1",
                        "name": "SD-WAN Controller",
                        "type": "orchestrator",
                        "description": "Central management system for SD-WAN",
                        "responsibilities": ["Policy management", "Traffic routing", "Network monitoring"]
                    },
                    {
                        "identifier": "CTRL-2",
                        "name": "Edge Gateway",
                        "type": "edge_controller",
                        "description": "Branch office gateway device",
                        "responsibilities": ["Local traffic control", "Security enforcement"]
                    }
                ],
                "controlled_processes": [
                    {
                        "identifier": "PROC-1",
                        "name": "Network Traffic Flow",
                        "type": "data_flow",
                        "description": "Enterprise data traffic between sites"
                    },
                    {
                        "identifier": "PROC-2",
                        "name": "Security Policy Enforcement",
                        "type": "security_process",
                        "description": "Application of security rules"
                    }
                ],
                "feedback_loops": [
                    {
                        "identifier": "FB-1",
                        "from": "PROC-1",
                        "to": "CTRL-1",
                        "type": "performance_metrics",
                        "description": "Network performance telemetry"
                    }
                ]
            },
            "hierarchy": {
                "levels": [
                    {
                        "level": 1,
                        "name": "Orchestration Layer",
                        "controllers": ["CTRL-1"]
                    },
                    {
                        "level": 2,
                        "name": "Edge Layer",
                        "controllers": ["CTRL-2"]
                    }
                ]
            },
            "control_actions": [
                {
                    "identifier": "CA-1",
                    "controller_identifier": "CTRL-1",
                    "process_identifier": "PROC-1",
                    "action_name": "Route Traffic",
                    "description": "Direct traffic through optimal WAN path",
                    "trigger": "Traffic arrival or policy change"
                },
                {
                    "identifier": "CA-2",
                    "controller_identifier": "CTRL-2",
                    "process_identifier": "PROC-2",
                    "action_name": "Apply Security Policy",
                    "description": "Enforce security rules on traffic",
                    "trigger": "New connection attempt"
                }
            ],
            "trust_boundaries": [
                {
                    "identifier": "TB-1",
                    "name": "Internet Perimeter",
                    "type": "network",
                    "description": "Boundary between enterprise and internet",
                    "crosses": [{"from": "CTRL-2", "to": "External Services"}],
                    "security_controls": ["Firewall", "IPS", "DDoS protection"]
                }
            ],
            "feedback_mechanisms": [
                {
                    "identifier": "FB-1",
                    "from_component": "PROC-1",
                    "to_component": "CTRL-1",
                    "type": "performance_metrics",
                    "description": "Network performance telemetry",
                    "data_transmitted": ["Link status", "Traffic statistics"],
                    "frequency": "Real-time streaming"
                }
            ],
            "summary": "Mock SD-WAN control structure analysis"
        }
        
        return ModelResponse(
            content=json.dumps(response_data),
            model="mock",
            usage={"prompt_tokens": 10, "completion_tokens": 100, "total_tokens": 110}
        )

# Replace the original MockModelClient
MockModelClient = MockModelClientFixed