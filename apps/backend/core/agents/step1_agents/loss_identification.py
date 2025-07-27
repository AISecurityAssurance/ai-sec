"""
Loss Identification Agent for STPA-Sec Step 1
"""
from typing import Dict, Any, List, Optional
import re
import json
from uuid import uuid4

from .base_step1 import BaseStep1Agent


class LossIdentificationAgent(BaseStep1Agent):
    """
    Identifies and analyzes losses (unacceptable outcomes)
    
    Responsibilities:
    - Identify mission-level losses
    - Categorize losses appropriately
    - Assess severity at mission level
    - Map capability losses
    - Identify loss dependencies
    """
    
    def get_agent_type(self) -> str:
        return "loss_identification"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and analyze losses"""
        await self.log_activity("Starting loss identification")
        
        system_description = context.get('system_description', '')
        mission_results = await self.get_prior_results(['mission_analyst'])
        
        # Extract different types of losses
        financial_losses = await self._identify_financial_losses(system_description, mission_results)
        regulatory_losses = await self._identify_regulatory_losses(system_description, mission_results)
        privacy_losses = await self._identify_privacy_losses(system_description, mission_results)
        reputation_losses = await self._identify_reputation_losses(system_description, mission_results)
        mission_losses = await self._identify_mission_losses(system_description, mission_results)
        
        # Combine all losses
        all_losses = financial_losses + regulatory_losses + privacy_losses + reputation_losses + mission_losses
        
        # Assign identifiers
        losses = []
        for i, loss in enumerate(all_losses):
            loss['identifier'] = f"L-{i+1}"
            losses.append(loss)
        
        # Identify loss dependencies
        dependencies = await self._identify_loss_dependencies(losses)
        
        # Create loss cascade analysis
        cascade_analysis = await self._analyze_loss_cascades(losses, dependencies)
        
        results = {
            "losses": losses,
            "loss_count": len(losses),
            "loss_categories": self._summarize_categories(losses),
            "dependencies": dependencies,
            "cascade_analysis": cascade_analysis,
            "severity_distribution": self._analyze_severity_distribution(losses)
        }
        
        await self.save_results(results)
        await self.log_activity("Completed loss identification", {
            "loss_count": len(losses),
            "dependency_count": len(dependencies)
        })
        
        return results
    
    async def _identify_financial_losses(self, description: str, mission_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify financial losses"""
        losses = []
        
        financial_indicators = [
            "financial", "money", "funds", "transaction", "payment",
            "revenue", "cost", "budget", "asset", "capital"
        ]
        
        if any(indicator in description.lower() for indicator in financial_indicators):
            # Unauthorized transactions
            losses.append({
                "description": "Loss of financial assets due to unauthorized transactions",
                "loss_category": "financial",
                "severity_classification": {
                    "magnitude": "catastrophic",
                    "scope": "organization_wide",
                    "duration": "long_term",
                    "reversibility": "difficult",
                    "detection_difficulty": "moderate"
                },
                "mission_impact": {
                    "primary_capability_loss": ["financial_integrity", "asset_protection"],
                    "cascading_effects": ["customer_trust", "regulatory_compliance"],
                    "stakeholder_harm": {
                        "customers": {"type": "financial_loss", "severity": "catastrophic"},
                        "organization": {"type": "revenue_loss", "severity": "major"}
                    }
                }
            })
            
            # Revenue loss
            losses.append({
                "description": "Loss of revenue due to service disruption",
                "loss_category": "financial",
                "severity_classification": {
                    "magnitude": "major",
                    "scope": "business_unit",
                    "duration": "medium_term",
                    "reversibility": "possible",
                    "detection_difficulty": "easy"
                },
                "mission_impact": {
                    "primary_capability_loss": ["revenue_generation", "business_continuity"],
                    "cascading_effects": ["market_position", "investor_confidence"],
                    "stakeholder_harm": {
                        "organization": {"type": "revenue_loss", "severity": "major"},
                        "shareholders": {"type": "value_loss", "severity": "moderate"}
                    }
                }
            })
        
        return losses
    
    async def _identify_regulatory_losses(self, description: str, mission_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify regulatory compliance losses"""
        losses = []
        
        # Check for regulatory frameworks
        regulatory_indicators = [
            "compliance", "regulation", "audit", "legal", "law",
            "PCI", "GDPR", "HIPAA", "SOX", "NERC"
        ]
        
        if any(indicator in description.upper() for indicator in regulatory_indicators):
            losses.append({
                "description": "Loss of regulatory compliance status",
                "loss_category": "regulatory",
                "severity_classification": {
                    "magnitude": "catastrophic",
                    "scope": "enterprise_wide",
                    "duration": "long_term",
                    "reversibility": "difficult",
                    "detection_difficulty": "easy"
                },
                "mission_impact": {
                    "primary_capability_loss": ["operational_authorization", "market_access"],
                    "cascading_effects": ["business_operations", "reputation"],
                    "stakeholder_harm": {
                        "regulators": {"type": "compliance_failure", "severity": "catastrophic"},
                        "organization": {"type": "operational_restriction", "severity": "catastrophic"}
                    }
                }
            })
        
        return losses
    
    async def _identify_privacy_losses(self, description: str, mission_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify privacy-related losses"""
        losses = []
        
        privacy_indicators = [
            "privacy", "personal", "PII", "confidential", "sensitive",
            "customer data", "user information", "private"
        ]
        
        if any(indicator in description.lower() for indicator in privacy_indicators):
            losses.append({
                "description": "Loss of customer privacy through unauthorized data exposure",
                "loss_category": "privacy",
                "severity_classification": {
                    "magnitude": "major",
                    "scope": "customer_wide",
                    "duration": "permanent",
                    "reversibility": "impossible",
                    "detection_difficulty": "hard"
                },
                "mission_impact": {
                    "primary_capability_loss": ["privacy_protection", "data_confidentiality"],
                    "cascading_effects": ["customer_trust", "legal_liability"],
                    "stakeholder_harm": {
                        "customers": {"type": "privacy_violation", "severity": "catastrophic"},
                        "organization": {"type": "legal_exposure", "severity": "major"}
                    }
                }
            })
        
        return losses
    
    async def _identify_reputation_losses(self, description: str, mission_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify reputation losses"""
        losses = []
        
        # Reputation is often a secondary effect
        if "customer" in description.lower() or "trust" in description.lower():
            losses.append({
                "description": "Loss of stakeholder trust and market confidence",
                "loss_category": "reputation",
                "severity_classification": {
                    "magnitude": "major",
                    "scope": "market_wide",
                    "duration": "long_term",
                    "reversibility": "very_difficult",
                    "detection_difficulty": "moderate"
                },
                "mission_impact": {
                    "primary_capability_loss": ["market_confidence", "stakeholder_trust"],
                    "cascading_effects": ["customer_acquisition", "partner_relationships"],
                    "stakeholder_harm": {
                        "customers": {"type": "trust_loss", "severity": "major"},
                        "partners": {"type": "confidence_loss", "severity": "moderate"},
                        "investors": {"type": "value_perception", "severity": "major"}
                    }
                }
            })
        
        return losses
    
    async def _identify_mission_losses(self, description: str, mission_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify mission-specific losses"""
        losses = []
        
        # Extract mission context
        mission_context = mission_results.get('mission_analyst', {}).get('mission_context', {})
        domain = mission_context.get('domain', 'general')
        
        if domain == 'financial_services' or 'banking' in description.lower():
            losses.append({
                "description": "Loss of ability to provide financial services to customers",
                "loss_category": "mission",
                "severity_classification": {
                    "magnitude": "catastrophic",
                    "scope": "mission_wide",
                    "duration": "variable",
                    "reversibility": "possible",
                    "detection_difficulty": "easy"
                },
                "mission_impact": {
                    "primary_capability_loss": ["service_delivery", "mission_fulfillment"],
                    "cascading_effects": ["customer_harm", "market_disruption"],
                    "stakeholder_harm": {
                        "customers": {"type": "service_denial", "severity": "catastrophic"},
                        "organization": {"type": "mission_failure", "severity": "catastrophic"}
                    }
                }
            })
        
        return losses
    
    async def _identify_loss_dependencies(self, losses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify dependencies between losses"""
        dependencies = []
        
        # Common dependency patterns
        for i, primary_loss in enumerate(losses):
            for j, dependent_loss in enumerate(losses):
                if i == j:
                    continue
                    
                # Financial losses often trigger reputation losses
                if (primary_loss['loss_category'] == 'financial' and 
                    dependent_loss['loss_category'] == 'reputation'):
                    dependencies.append({
                        "id": str(uuid4()),
                        "primary_loss_id": primary_loss['identifier'],
                        "dependent_loss_id": dependent_loss['identifier'],
                        "dependency_type": "triggers",
                        "dependency_strength": "likely",
                        "time_relationship": {
                            "sequence": "delayed",
                            "typical_delay": "days_to_weeks",
                            "persistence": "sustained"
                        },
                        "rationale": "Financial losses become public knowledge affecting reputation"
                    })
                
                # Regulatory losses almost certainly trigger reputation losses
                if (primary_loss['loss_category'] == 'regulatory' and 
                    dependent_loss['loss_category'] == 'reputation'):
                    dependencies.append({
                        "id": str(uuid4()),
                        "primary_loss_id": primary_loss['identifier'],
                        "dependent_loss_id": dependent_loss['identifier'],
                        "dependency_type": "triggers",
                        "dependency_strength": "certain",
                        "time_relationship": {
                            "sequence": "immediate",
                            "typical_delay": "hours_to_days",
                            "persistence": "sustained"
                        },
                        "rationale": "Regulatory violations are publicly disclosed"
                    })
                
                # Privacy losses enable financial losses
                if (primary_loss['loss_category'] == 'privacy' and 
                    dependent_loss['loss_category'] == 'financial'):
                    dependencies.append({
                        "id": str(uuid4()),
                        "primary_loss_id": primary_loss['identifier'],
                        "dependent_loss_id": dependent_loss['identifier'],
                        "dependency_type": "enables",
                        "dependency_strength": "possible",
                        "time_relationship": {
                            "sequence": "concurrent",
                            "typical_delay": "immediate",
                            "persistence": "variable"
                        },
                        "rationale": "Exposed data can be used for financial fraud"
                    })
        
        return dependencies
    
    async def _analyze_loss_cascades(self, losses: List[Dict[str, Any]], 
                                    dependencies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze potential loss cascade chains"""
        cascades = {
            "primary_losses": [],
            "cascade_chains": [],
            "max_cascade_depth": 0
        }
        
        # Identify primary losses (no incoming dependencies)
        dependent_loss_ids = {dep['dependent_loss_id'] for dep in dependencies}
        primary_losses = [loss for loss in losses 
                         if loss['identifier'] not in dependent_loss_ids]
        cascades['primary_losses'] = [loss['identifier'] for loss in primary_losses]
        
        # Build cascade chains
        for primary_loss in primary_losses:
            chain = self._build_cascade_chain(primary_loss['identifier'], dependencies, losses)
            if len(chain) > 1:
                cascades['cascade_chains'].append({
                    "chain": chain,
                    "trigger": primary_loss['identifier'],
                    "terminal_losses": chain[-1:],
                    "chain_length": len(chain)
                })
        
        # Calculate max cascade depth
        if cascades['cascade_chains']:
            cascades['max_cascade_depth'] = max(
                chain['chain_length'] for chain in cascades['cascade_chains']
            )
        
        return cascades
    
    def _build_cascade_chain(self, loss_id: str, dependencies: List[Dict[str, Any]], 
                            losses: List[Dict[str, Any]], visited: Optional[set] = None) -> List[str]:
        """Build a cascade chain starting from a loss"""
        if visited is None:
            visited = set()
            
        if loss_id in visited:
            return []
            
        visited.add(loss_id)
        chain = [loss_id]
        
        # Find dependent losses
        for dep in dependencies:
            if dep['primary_loss_id'] == loss_id:
                sub_chain = self._build_cascade_chain(
                    dep['dependent_loss_id'], dependencies, losses, visited
                )
                if sub_chain:
                    chain.extend(sub_chain)
        
        return chain
    
    def _summarize_categories(self, losses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Summarize loss categories"""
        categories = {}
        for loss in losses:
            category = loss['loss_category']
            categories[category] = categories.get(category, 0) + 1
        return categories
    
    def _analyze_severity_distribution(self, losses: List[Dict[str, Any]]) -> Dict[str, int]:
        """Analyze severity distribution"""
        distribution = {
            "catastrophic": 0,
            "major": 0,
            "moderate": 0,
            "minor": 0
        }
        
        for loss in losses:
            magnitude = loss['severity_classification']['magnitude']
            if magnitude in distribution:
                distribution[magnitude] += 1
                
        return distribution
    
    def validate_abstraction_level(self, content: str) -> bool:
        """Validate loss maintains mission-level abstraction"""
        # Losses should describe outcomes, not mechanisms
        mechanism_words = ["attack", "exploit", "vulnerability", "breach", "hack"]
        content_lower = content.lower()
        
        if any(word in content_lower for word in mechanism_words):
            return False
            
        return not self.is_implementation_detail(content)