"""Mock model provider for testing without API keys."""
import json
import asyncio
from typing import Dict, Any, List, Optional
from core.model_providers.base import ModelProvider, ModelResponse


class MockModelProvider(ModelProvider):
    """Mock provider that returns pre-defined responses for testing."""
    
    def __init__(self, api_key: str = "mock", **kwargs):
        super().__init__(api_key, **kwargs)
        self.name = "mock"
        
    async def query(self, prompt: str, system_prompt: Optional[str] = None, 
                   temperature: float = 0.7, max_tokens: int = 4000) -> ModelResponse:
        """Return mock responses based on prompt content."""
        # Simulate some processing time
        await asyncio.sleep(0.1)
        
        # Generate mock response based on prompt content
        prompt_lower = prompt.lower()
        
        # Look for key phrases that indicate what type of response is needed
        if any(phrase in prompt_lower for phrase in ["control structure", "identify control structure", "controllers**: components that make decisions", "task: identify control structure"]):
            response = self._generate_control_structure_response()
        elif any(phrase in prompt_lower for phrase in ["control action", "map control actions", "identify control actions", "task: map control actions"]):
            response = self._generate_control_actions_response()
        elif any(phrase in prompt_lower for phrase in ["trust boundar", "security boundaries", "analyze trust boundaries", "task: identify trust boundaries"]):
            response = self._generate_trust_boundaries_response()
        elif any(phrase in prompt_lower for phrase in ["process model", "controller's view", "state variables"]):
            response = self._generate_process_model_response()
        elif any(phrase in prompt_lower for phrase in ["control context", "when and under what conditions", "execution mechanics"]):
            response = self._generate_control_context_response()
        elif any(phrase in prompt_lower for phrase in ["system description", "comprehensive system description"]):
            response = self._generate_system_description_response()
        elif any(phrase in prompt_lower for phrase in ["feedback", "feedback mechanism", "information flow", "task: identify feedback mechanisms"]):
            response = self._generate_feedback_response()
        else:
            # Default response with basic structure
            response = json.dumps({
                "message": "Mock response for testing",
                "prompt_length": len(prompt),
                "contains_json": "json" in prompt_lower,
                "keywords_found": [kw for kw in ["control", "system", "component", "process"] if kw in prompt_lower]
            })
        
        return ModelResponse(
            content=response,
            usage={
                "prompt_tokens": len(prompt.split()),
                "completion_tokens": len(response.split()),
                "total_tokens": len(prompt.split()) + len(response.split())
            },
            model="mock-model",
            finish_reason="stop"
        )
    
    async def verify_connection(self) -> bool:
        """Always return True for mock provider."""
        return True
    
    def _generate_control_structure_response(self) -> str:
        """Generate mock control structure response."""
        return json.dumps({
            "components": {
                "controllers": [
                    {
                        "identifier": "CTRL-1",
                        "name": "SD-WAN Controller",
                        "type": "orchestrator",
                        "description": "Central management system for SD-WAN network",
                        "responsibilities": ["Policy management", "Traffic routing", "Network monitoring"]
                    },
                    {
                        "identifier": "CTRL-2", 
                        "name": "Edge Gateway",
                        "type": "edge_controller",
                        "description": "Branch office gateway device",
                        "responsibilities": ["Local traffic control", "Security enforcement", "WAN optimization"]
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
                        "description": "Application of security rules to traffic"
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
            "description": "SD-WAN control structure with centralized orchestration and distributed edge control"
        })
    
    def _generate_control_actions_response(self) -> str:
        """Generate mock control actions response."""
        return json.dumps({
            "control_actions": [
                {
                    "identifier": "CA-1",
                    "controller_identifier": "CTRL-1",
                    "process_identifier": "PROC-1",
                    "action_name": "Route Traffic",
                    "description": "Direct traffic through optimal WAN path",
                    "trigger": "Traffic arrival or policy change",
                    "constraints": ["Available bandwidth", "Latency requirements", "Security policy"]
                },
                {
                    "identifier": "CA-2",
                    "controller_identifier": "CTRL-2",
                    "process_identifier": "PROC-2",
                    "action_name": "Apply Security Policy",
                    "description": "Enforce security rules on traffic",
                    "trigger": "New connection attempt",
                    "constraints": ["Policy rules", "Threat intelligence", "Performance impact"]
                }
            ],
            "summary": "Identified 2 primary control actions for SD-WAN system"
        })
    
    def _generate_trust_boundaries_response(self) -> str:
        """Generate mock trust boundaries response."""
        return json.dumps({
            "trust_boundaries": [
                {
                    "identifier": "TB-1",
                    "name": "Internet Perimeter",
                    "type": "network",
                    "description": "Boundary between enterprise network and public internet",
                    "crosses": [
                        {"from": "CTRL-2", "to": "External Services"}
                    ],
                    "security_controls": ["Firewall", "IPS", "DDoS protection"]
                }
            ],
            "analysis": "One major trust boundary identified at network perimeter"
        })
    
    def _generate_process_model_response(self) -> str:
        """Generate mock process model response."""
        return json.dumps({
            "models": [
                {
                    "identifier": "PM-1",
                    "controller_id": "CTRL-1",
                    "process_id": "PROC-1",
                    "state_variables": [
                        {
                            "name": "link_status",
                            "type": "enum",
                            "description": "Status of WAN links",
                            "update_mechanism": "Periodic health checks",
                            "potential_issues": ["Stale status during network partition"]
                        }
                    ],
                    "assumptions": ["Links report status accurately", "Telemetry is timely"],
                    "update_frequency": "periodic",
                    "staleness_risk": "medium"
                }
            ],
            "algorithms": [
                {
                    "identifier": "ALG-1",
                    "controller_id": "CTRL-1",
                    "name": "Path Selection Algorithm",
                    "description": "Selects optimal WAN path for traffic",
                    "constraints": [
                        {
                            "type": "performance",
                            "constraint": "Latency < 100ms for voice traffic",
                            "enforcement": "Path scoring and prioritization",
                            "violation_impact": "Quality degradation"
                        }
                    ],
                    "decision_logic": "Multi-factor scoring based on latency, bandwidth, and cost",
                    "conflict_resolution": "Priority-based with fallback options"
                }
            ],
            "insights": {
                "model_coverage": "Good coverage of primary control elements",
                "algorithm_sophistication": "Moderate complexity with clear decision logic",
                "information_dependencies": "Heavy reliance on real-time telemetry",
                "timing_characteristics": "Sub-second decision requirements for traffic routing",
                "coordination_needs": "Controller-edge coordination critical"
            },
            "summary": "Process models show typical SD-WAN control patterns"
        })
    
    def _generate_control_context_response(self) -> str:
        """Generate mock control context response."""
        return json.dumps({
            "control_contexts": [
                {
                    "control_action_id": "CA-1",
                    "execution_context": {
                        "triggers": ["New traffic flow detected", "Link status change", "Policy update"],
                        "preconditions": ["Controller has current network state", "At least one link available"],
                        "environmental_factors": ["Time of day", "Business criticality"],
                        "timing_requirements": {
                            "frequency": "Per-flow basis",
                            "response_time": "< 50ms",
                            "duration": "Until flow completes"
                        }
                    },
                    "decision_logic": {
                        "inputs_evaluated": ["Application type", "Link metrics", "Security policy", "Cost factors"],
                        "decision_criteria": "Weighted scoring with policy overrides",
                        "priority": "high",
                        "conflict_resolution": "Policy precedence then performance optimization"
                    },
                    "applicable_modes": ["Normal Operation", "Failover Mode"]
                }
            ],
            "operational_modes": [
                {
                    "mode_name": "Normal Operation",
                    "description": "All WAN links functioning normally",
                    "entry_conditions": ["All primary links up", "No security incidents"],
                    "exit_conditions": ["Link failure", "Security breach detected"],
                    "active_controllers": ["CTRL-1", "CTRL-2"],
                    "available_actions": ["CA-1", "CA-2"],
                    "mode_constraints": ["Use all available paths", "Optimize for performance"]
                }
            ],
            "mode_transitions": [],
            "analysis_notes": "Control contexts well-defined with clear operational modes"
        })
    
    def _generate_system_description_response(self) -> str:
        """Generate mock system description response."""
        return json.dumps({
            "system_overview": {
                "name": "Enterprise SD-WAN System",
                "type": "Software-Defined Wide Area Network",
                "purpose": "Connect enterprise locations with optimized, secure connectivity",
                "scope": "Branch offices, data centers, and cloud resources",
                "operational_context": "24/7 business operations across multiple geographic regions"
            },
            "architecture": {
                "deployment_model": "Hybrid cloud with on-premises edges",
                "topology": "Hub-and-spoke with mesh capabilities",
                "key_components": ["Orchestrator", "Edge devices", "Analytics engine"]
            },
            "components": [
                {
                    "name": "SD-WAN Orchestrator",
                    "type": "Central Controller",
                    "responsibilities": ["Policy management", "Network orchestration", "Analytics"],
                    "interfaces": ["REST API", "Web UI", "CLI"],
                    "deployment": "Cloud-based SaaS"
                }
            ],
            "interactions": [
                {
                    "from": "Orchestrator",
                    "to": "Edge Gateway",
                    "type": "Control Channel",
                    "protocol": "Encrypted REST/WebSocket",
                    "purpose": "Policy distribution and telemetry collection"
                }
            ],
            "control_hierarchy": {
                "levels": 2,
                "centralized_functions": ["Policy definition", "Analytics", "Monitoring"],
                "distributed_functions": ["Traffic forwarding", "Local optimization", "Security enforcement"]
            },
            "operational_flows": [
                {
                    "name": "Application Traffic Flow",
                    "description": "Business application data between sites",
                    "path": "Branch -> Edge -> WAN -> Edge -> Data Center",
                    "control_points": ["Branch edge", "DC edge"]
                }
            ],
            "key_characteristics": {
                "scalability": "Supports 1000+ sites",
                "performance": "Sub-second path switching",
                "security": "End-to-end encryption with micro-segmentation",
                "reliability": "Active-active redundancy with automatic failover"
            }
        })
    
    def _generate_feedback_response(self) -> str:
        """Generate mock feedback mechanisms response."""
        return json.dumps({
            "feedback_mechanisms": [
                {
                    "identifier": "FB-1",
                    "from_component": "PROC-1",
                    "to_component": "CTRL-1",
                    "type": "performance_metrics",
                    "description": "Network performance telemetry",
                    "data_transmitted": ["Link status", "Traffic statistics", "Error rates"],
                    "frequency": "Real-time streaming",
                    "critical_for_control": True
                },
                {
                    "identifier": "FB-2",
                    "from_component": "PROC-2",
                    "to_component": "CTRL-2",
                    "type": "security_alerts",
                    "description": "Security event notifications",
                    "data_transmitted": ["Threat detections", "Policy violations", "Anomalies"],
                    "frequency": "Event-driven",
                    "critical_for_control": True
                }
            ],
            "summary": "Identified 2 feedback mechanisms providing critical control information"
        })