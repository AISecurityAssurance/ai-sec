"""
Hazard State Identification Agent for STPA-Sec Step 1
"""
from typing import Dict, Any, List, Optional, Tuple
import re
import json
from uuid import uuid4

from .base_step1 import BaseStep1Agent


class HazardIdentificationAgent(BaseStep1Agent):
    """
    Identifies hazardous system states that could lead to losses
    
    Responsibilities:
    - Identify system states (not actions)
    - Map states to potential losses
    - Analyze temporal aspects
    - Consider environmental factors
    """
    
    def get_agent_type(self) -> str:
        return "hazard_identification"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and analyze hazardous system states"""
        await self.log_activity("Starting hazard identification")
        
        system_description = context.get('system_description', '')
        prior_results = await self.get_prior_results(['mission_analyst', 'loss_identification'])
        
        losses = prior_results.get('loss_identification', {}).get('losses', [])
        mission_context = prior_results.get('mission_analyst', {}).get('mission_context', {})
        
        # Identify hazards by category
        integrity_hazards = await self._identify_integrity_hazards(system_description, losses, mission_context)
        confidentiality_hazards = await self._identify_confidentiality_hazards(system_description, losses, mission_context)
        availability_hazards = await self._identify_availability_hazards(system_description, losses, mission_context)
        capability_hazards = await self._identify_capability_hazards(system_description, losses, mission_context)
        
        # Combine all hazards
        all_hazards = integrity_hazards + confidentiality_hazards + availability_hazards + capability_hazards
        
        # Assign identifiers
        hazards = []
        for i, hazard in enumerate(all_hazards):
            hazard['identifier'] = f"H-{i+1}"
            hazards.append(hazard)
        
        # Create hazard-loss mappings
        mappings = await self._create_hazard_loss_mappings(hazards, losses)
        
        # Analyze temporal exposure
        temporal_analysis = await self._analyze_temporal_exposure(hazards)
        
        # Analyze environmental factors
        environmental_analysis = await self._analyze_environmental_factors(hazards, mission_context)
        
        results = {
            "hazards": hazards,
            "hazard_count": len(hazards),
            "hazard_categories": self._summarize_categories(hazards),
            "hazard_loss_mappings": mappings,
            "temporal_analysis": temporal_analysis,
            "environmental_analysis": environmental_analysis,
            "coverage_analysis": await self._analyze_loss_coverage(hazards, losses, mappings)
        }
        
        await self.save_results(results)
        await self.log_activity("Completed hazard identification", {
            "hazard_count": len(hazards),
            "mapping_count": len(mappings)
        })
        
        return results
    
    async def _identify_integrity_hazards(self, description: str, losses: List[Dict[str, Any]], 
                                         mission_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify integrity-related hazardous states"""
        hazards = []
        
        # Common integrity concerns
        integrity_patterns = [
            ("authentication", "System operates with compromised identity verification integrity"),
            ("authorization", "System operates without proper access control integrity"),
            ("transaction", "System operates without transaction integrity assurance"),
            ("data integrity", "System operates with compromised data integrity mechanisms")
        ]
        
        for keyword, state_description in integrity_patterns:
            if keyword in description.lower():
                hazards.append({
                    "description": state_description,
                    "hazard_category": "integrity_compromised",
                    "affected_system_property": self._extract_affected_property(state_description),
                    "environmental_factors": {
                        "operational_conditions": {
                            "normal": {"impact": "moderate", "likelihood": "rare"},
                            "degraded": {"impact": "high", "likelihood": "possible"},
                            "emergency": {"impact": "catastrophic", "likelihood": "likely"}
                        },
                        "threat_conditions": {
                            "baseline": {"system_resilience": "adequate"},
                            "elevated": {"system_resilience": "stressed"},
                            "severe": {"system_resilience": "compromised"}
                        }
                    },
                    "temporal_nature": {
                        "existence": "always",
                        "mission_relevance": "Creates persistent vulnerability to mission compromise"
                    }
                })
        
        return hazards
    
    async def _identify_confidentiality_hazards(self, description: str, losses: List[Dict[str, Any]], 
                                               mission_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify confidentiality-related hazardous states"""
        hazards = []
        
        confidentiality_keywords = ["privacy", "confidential", "sensitive", "encryption", "data protection"]
        
        if any(keyword in description.lower() for keyword in confidentiality_keywords):
            hazards.append({
                "description": "System operates with data protection mechanisms in compromised state",
                "hazard_category": "confidentiality_breached",
                "affected_system_property": "data_protection",
                "environmental_factors": {
                    "operational_conditions": {
                        "normal": {"impact": "high", "likelihood": "very_rare"},
                        "degraded": {"impact": "catastrophic", "likelihood": "possible"},
                        "emergency": {"impact": "catastrophic", "likelihood": "likely"}
                    },
                    "threat_conditions": {
                        "baseline": {"exposure_window": "limited"},
                        "elevated": {"exposure_window": "extended"},
                        "severe": {"exposure_window": "continuous"}
                    }
                },
                "temporal_nature": {
                    "existence": "always",
                    "mission_relevance": "Exposes mission-critical information continuously"
                }
            })
        
        return hazards
    
    async def _identify_availability_hazards(self, description: str, losses: List[Dict[str, Any]], 
                                           mission_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify availability-related hazardous states"""
        hazards = []
        
        availability_keywords = ["availability", "service", "uptime", "24/7", "real-time"]
        
        if any(keyword in description.lower() for keyword in availability_keywords):
            hazards.append({
                "description": "System operates in degraded state preventing mission accomplishment",
                "hazard_category": "availability_degraded",
                "affected_system_property": "service_availability",
                "environmental_factors": {
                    "operational_conditions": {
                        "normal": {"impact": "moderate", "likelihood": "rare"},
                        "peak": {"impact": "high", "likelihood": "possible"},
                        "crisis": {"impact": "catastrophic", "likelihood": "likely"}
                    },
                    "threat_conditions": {
                        "baseline": {"attack_surface": "normal"},
                        "elevated": {"attack_surface": "expanded"},
                        "severe": {"attack_surface": "maximum"}
                    }
                },
                "temporal_nature": {
                    "existence": "always",
                    "mission_relevance": "Directly prevents mission execution"
                }
            })
        
        return hazards
    
    async def _identify_capability_hazards(self, description: str, losses: List[Dict[str, Any]], 
                                          mission_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify capability loss hazardous states"""
        hazards = []
        
        # Look for specific capabilities mentioned
        if "fraud" in description.lower() or "detection" in description.lower():
            hazards.append({
                "description": "System operates without effective anomaly detection capability",
                "hazard_category": "capability_loss",
                "affected_system_property": "operational_capability",
                "environmental_factors": {
                    "operational_conditions": {
                        "normal": {"detection_gap": "minimal"},
                        "high_volume": {"detection_gap": "moderate"},
                        "attack": {"detection_gap": "severe"}
                    },
                    "threat_conditions": {
                        "baseline": {"false_negative_rate": "acceptable"},
                        "elevated": {"false_negative_rate": "concerning"},
                        "severe": {"false_negative_rate": "critical"}
                    }
                },
                "temporal_nature": {
                    "existence": "periodic",
                    "when_present": "During model updates, high-volume periods, or targeted attacks",
                    "mission_relevance": "Creates windows of vulnerability to mission compromise"
                }
            })
        
        if "decision" in description.lower() or "automated" in description.lower():
            hazards.append({
                "description": "System operates with compromised decision-making integrity",
                "hazard_category": "capability_loss",
                "affected_system_property": "operational_capability",
                "environmental_factors": {
                    "operational_conditions": {
                        "normal": {"decision_accuracy": "high"},
                        "degraded": {"decision_accuracy": "questionable"},
                        "compromised": {"decision_accuracy": "unreliable"}
                    },
                    "threat_conditions": {
                        "baseline": {"manipulation_risk": "low"},
                        "elevated": {"manipulation_risk": "moderate"},
                        "severe": {"manipulation_risk": "high"}
                    }
                },
                "temporal_nature": {
                    "existence": "always",
                    "mission_relevance": "Undermines mission decision quality"
                }
            })
        
        return hazards
    
    def _extract_affected_property(self, state_description: str) -> str:
        """Extract the affected system property from state description"""
        property_map = {
            "identity verification": "transaction_integrity",
            "access control": "transaction_integrity",
            "transaction": "transaction_integrity",
            "data integrity": "data_protection",
            "data protection": "data_protection",
            "service": "service_availability",
            "detection": "operational_capability",
            "decision": "operational_capability",
            "authentication": "transaction_integrity",
            "authorization": "transaction_integrity"
        }
        
        desc_lower = state_description.lower()
        for keyword, property_name in property_map.items():
            if keyword in desc_lower:
                return property_name
                
        return "mission_effectiveness"
    
    async def _create_hazard_loss_mappings(self, hazards: List[Dict[str, Any]], 
                                          losses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create mappings between hazards and losses"""
        mappings = []
        
        for hazard in hazards:
            for loss in losses:
                strength, rationale = self._assess_hazard_loss_relationship(hazard, loss)
                
                if strength:
                    mappings.append({
                        "id": str(uuid4()),
                        "hazard_id": hazard['identifier'],
                        "loss_id": loss['identifier'],
                        "relationship_strength": strength,
                        "rationale": rationale,
                        "conditions": self._identify_enabling_conditions(hazard, loss)
                    })
        
        return mappings
    
    def _assess_hazard_loss_relationship(self, hazard: Dict[str, Any], 
                                       loss: Dict[str, Any]) -> Tuple[Optional[str], str]:
        """Assess the relationship between a hazard and loss"""
        hazard_category = hazard['hazard_category']
        loss_category = loss['loss_category']
        
        # Direct relationships
        direct_relationships = {
            ('integrity_compromised', 'financial'): (
                'direct',
                'Compromised integrity directly enables financial losses'
            ),
            ('confidentiality_breached', 'privacy'): (
                'direct',
                'Confidentiality breach directly causes privacy loss'
            ),
            ('availability_degraded', 'mission'): (
                'direct',
                'Availability loss directly prevents mission accomplishment'
            ),
            ('capability_loss', 'financial'): (
                'direct',
                'Lost detection capability enables financial losses'
            )
        }
        
        # Conditional relationships
        conditional_relationships = {
            ('integrity_compromised', 'reputation'): (
                'conditional',
                'Integrity compromise may lead to reputation loss if discovered'
            ),
            ('confidentiality_breached', 'regulatory'): (
                'conditional',
                'Confidentiality breach triggers regulatory loss if data is regulated'
            ),
            ('availability_degraded', 'financial'): (
                'conditional',
                'Availability loss causes financial impact through SLA violations'
            )
        }
        
        # Check for matches
        key = (hazard_category, loss_category)
        if key in direct_relationships:
            return direct_relationships[key]
        elif key in conditional_relationships:
            return conditional_relationships[key]
        
        # Check for any integrity hazard leading to regulatory loss
        if hazard_category == 'integrity_compromised' and loss_category == 'regulatory':
            return 'conditional', 'Integrity failures may violate regulatory requirements'
        
        # Check for any hazard leading to reputation loss
        if loss_category == 'reputation':
            return 'indirect', 'Any significant hazard realization can damage reputation'
        
        return None, ""
    
    def _identify_enabling_conditions(self, hazard: Dict[str, Any], 
                                    loss: Dict[str, Any]) -> List[str]:
        """Identify conditions that enable hazard to lead to loss"""
        conditions = []
        
        # Environmental conditions
        env_factors = hazard.get('environmental_factors', {})
        if 'degraded' in env_factors.get('operational_conditions', {}):
            conditions.append("System operating in degraded mode")
        
        # Temporal conditions
        temporal = hazard.get('temporal_nature', {})
        if temporal.get('existence') == 'periodic':
            conditions.append(f"During: {temporal.get('when_present', 'specific time windows')}")
        
        # Threat conditions
        if 'severe' in env_factors.get('threat_conditions', {}):
            conditions.append("Under active adversarial pressure")
        
        return conditions
    
    async def _analyze_temporal_exposure(self, hazards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze temporal aspects of hazards"""
        analysis = {
            "always_present": [],
            "periodic": [],
            "conditional": [],
            "coverage_gaps": []
        }
        
        for hazard in hazards:
            temporal = hazard.get('temporal_nature', {})
            existence = temporal.get('existence', 'always')
            
            if existence == 'always':
                analysis['always_present'].append({
                    "hazard_id": hazard['identifier'],
                    "description": hazard['description']
                })
            elif existence == 'periodic':
                analysis['periodic'].append({
                    "hazard_id": hazard['identifier'],
                    "description": hazard['description'],
                    "when": temporal.get('when_present', 'unspecified')
                })
            else:
                analysis['conditional'].append({
                    "hazard_id": hazard['identifier'],
                    "description": hazard['description'],
                    "conditions": temporal.get('conditions', [])
                })
        
        # Identify coverage gaps
        if analysis['periodic']:
            analysis['coverage_gaps'].append({
                "gap_type": "temporal",
                "description": "Periodic hazards create vulnerability windows",
                "affected_hazards": [h['hazard_id'] for h in analysis['periodic']]
            })
        
        return analysis
    
    async def _analyze_environmental_factors(self, hazards: List[Dict[str, Any]], 
                                           mission_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze environmental factors affecting hazards"""
        analysis = {
            "operational_sensitivity": {},
            "threat_sensitivity": {},
            "combined_risk_scenarios": []
        }
        
        for hazard in hazards:
            env_factors = hazard.get('environmental_factors', {})
            
            # Operational sensitivity
            ops_conditions = env_factors.get('operational_conditions', {})
            if ops_conditions:
                worst_case = max(ops_conditions.values(), 
                               key=lambda x: self._severity_score(x.get('impact', 'low')))
                analysis['operational_sensitivity'][hazard['identifier']] = {
                    "worst_case_condition": list(ops_conditions.keys())[
                        list(ops_conditions.values()).index(worst_case)
                    ],
                    "impact": worst_case.get('impact', 'unknown')
                }
            
            # Threat sensitivity
            threat_conditions = env_factors.get('threat_conditions', {})
            if threat_conditions:
                analysis['threat_sensitivity'][hazard['identifier']] = {
                    "escalation_pattern": self._analyze_threat_escalation(threat_conditions)
                }
        
        # Combined risk scenarios
        high_risk_hazards = [
            h_id for h_id, sens in analysis['operational_sensitivity'].items()
            if sens['impact'] in ['high', 'catastrophic']
        ]
        
        if high_risk_hazards:
            analysis['combined_risk_scenarios'].append({
                "scenario": "Multiple high-impact hazards under stress",
                "hazards": high_risk_hazards,
                "risk_level": "extreme"
            })
        
        return analysis
    
    def _severity_score(self, severity: str) -> int:
        """Convert severity to numeric score"""
        scores = {
            "low": 1,
            "moderate": 2,
            "high": 3,
            "catastrophic": 4
        }
        return scores.get(severity.lower(), 0)
    
    def _analyze_threat_escalation(self, threat_conditions: Dict[str, Any]) -> str:
        """Analyze how threats escalate"""
        if 'severe' in threat_conditions:
            severe = threat_conditions['severe']
            if 'overwhelmed' in str(severe).lower():
                return "System degrades catastrophically under severe threats"
            elif 'compromised' in str(severe).lower():
                return "System integrity fails under severe threats"
        
        return "System shows progressive degradation with threat escalation"
    
    async def _analyze_loss_coverage(self, hazards: List[Dict[str, Any]], 
                                   losses: List[Dict[str, Any]], 
                                   mappings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how well hazards cover identified losses"""
        coverage = {
            "covered_losses": [],
            "uncovered_losses": [],
            "coverage_percentage": 0,
            "loss_hazard_ratio": {}
        }
        
        # Find covered losses
        covered_loss_set = set()
        for mapping in mappings:
            covered_loss_set.add(mapping['loss_id'])
        coverage['covered_losses'] = list(covered_loss_set)
        
        # Find uncovered losses
        all_loss_ids = {loss['identifier'] for loss in losses}
        uncovered_ids = all_loss_ids - covered_loss_set
        coverage['uncovered_losses'] = list(uncovered_ids)
        
        # Calculate coverage
        if losses:
            coverage['coverage_percentage'] = (
                len(covered_loss_set) / len(losses) * 100
            )
        
        # Calculate loss-hazard ratio
        for loss in losses:
            hazard_count = sum(1 for m in mappings if m['loss_id'] == loss['identifier'])
            coverage['loss_hazard_ratio'][loss['identifier']] = hazard_count
        
        return coverage
    
    def _summarize_categories(self, hazards: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize hazard categories"""
        categories = {}
        for hazard in hazards:
            category = hazard['hazard_category']
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def validate_abstraction_level(self, content: str) -> bool:
        """Validate hazard maintains system state abstraction"""
        # Hazards must describe states, not actions
        action_words = ["attack", "exploit", "injection", "overflow", "bypass"]
        content_lower = content.lower()
        
        if any(word in content_lower for word in action_words):
            return False
        
        # Must use state language
        state_indicators = ["operates", "state", "condition", "mode"]
        has_state_language = any(word in content_lower for word in state_indicators)
        
        return has_state_language and not self.is_implementation_detail(content)