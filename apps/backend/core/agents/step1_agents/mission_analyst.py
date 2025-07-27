"""
Mission Analyst Agent for STPA-Sec Step 1
"""
from typing import Dict, Any, List
import re
import json

from .base_step1 import BaseStep1Agent


class MissionAnalystAgent(BaseStep1Agent):
    """
    Analyzes and structures the system's mission
    
    Responsibilities:
    - Extract PURPOSE (what the system does)
    - Extract METHOD (how it achieves purpose - abstract)
    - Extract GOALS (why it matters)
    - Ensure mission-level language
    """
    
    def get_agent_type(self) -> str:
        return "mission_analyst"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system mission from description"""
        await self.log_activity("Starting mission analysis")
        
        system_description = context.get('system_description', '')
        
        # Extract components
        purpose = await self._extract_purpose(system_description)
        method = await self._extract_method(system_description)
        goals = await self._extract_goals(system_description)
        
        # Build problem statement
        problem_statement = {
            "purpose_what": purpose,
            "method_how": method,
            "goals_why": goals,
            "full_statement": f"A System to {purpose} by means of {method} in order to {goals}"
        }
        
        # Extract mission context
        mission_context = await self._extract_mission_context(system_description)
        
        # Extract operational constraints
        operational_constraints = await self._extract_operational_constraints(system_description)
        
        # Extract environmental assumptions
        environmental_assumptions = await self._extract_environmental_assumptions(system_description)
        
        results = {
            "problem_statement": problem_statement,
            "mission_context": mission_context,
            "operational_constraints": operational_constraints,
            "environmental_assumptions": environmental_assumptions,
            "abstraction_validated": True
        }
        
        # Validate abstraction level
        for key, value in problem_statement.items():
            if isinstance(value, str) and self.is_implementation_detail(value):
                results["abstraction_warnings"] = results.get("abstraction_warnings", [])
                results["abstraction_warnings"].append(f"{key} contains implementation details")
                results["abstraction_validated"] = False
        
        await self.save_results(results)
        await self.log_activity("Completed mission analysis", results)
        
        return results
    
    async def _extract_purpose(self, description: str) -> str:
        """Extract the system's purpose (WHAT it does)"""
        # Look for purpose indicators
        purpose_patterns = [
            r"purpose is to (.+?)(?:\.|,|by|through)",
            r"designed to (.+?)(?:\.|,|by|through)",
            r"system that (.+?)(?:\.|,|by|through)",
            r"platform for (.+?)(?:\.|,|by|through)",
            r"enables (.+?)(?:\.|,|by|through)"
        ]
        
        for pattern in purpose_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                purpose = match.group(1).strip()
                # Clean up and ensure mission-level language
                purpose = self.extract_mission_language(purpose)
                return purpose
        
        # Fallback: extract from first sentence
        first_sentence = description.split('.')[0]
        purpose = self.extract_mission_language(first_sentence)
        return purpose
    
    async def _extract_method(self, description: str) -> str:
        """Extract the method (HOW it achieves purpose - abstract level)"""
        method_patterns = [
            r"by means of (.+?)(?:\.|,|in order to)",
            r"through (.+?)(?:\.|,|to)",
            r"via (.+?)(?:\.|,|to)",
            r"using (.+?)(?:\.|,|to)"
        ]
        
        for pattern in method_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                method = match.group(1).strip()
                # Ensure abstract language
                method = self.extract_mission_language(method)
                return method
        
        # Fallback: infer from description
        if "banking" in description.lower():
            return "controlled access to financial services with transaction integrity assurance"
        elif "medical" in description.lower():
            return "controlled delivery of healthcare services with patient safety assurance"
        else:
            return "controlled system operations with integrity assurance"
    
    async def _extract_goals(self, description: str) -> str:
        """Extract the goals (WHY it matters)"""
        goal_patterns = [
            r"in order to (.+?)(?:\.|$)",
            r"to achieve (.+?)(?:\.|$)",
            r"ensuring (.+?)(?:\.|$)",
            r"while (.+?)(?:\.|$)"
        ]
        
        goals = []
        for pattern in goal_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            for match in matches:
                goal = self.extract_mission_language(match.strip())
                if not self.is_prevention_language(goal):
                    goals.append(goal)
        
        if goals:
            return " and ".join(goals[:3])  # Limit to 3 main goals
        
        # Fallback based on domain
        if "banking" in description.lower():
            return "enable customer financial management while ensuring regulatory compliance and maintaining market trust"
        else:
            return "achieve mission objectives while maintaining stakeholder trust"
    
    async def _extract_mission_context(self, description: str) -> Dict[str, Any]:
        """Extract mission context information"""
        context = {
            "domain": self._identify_domain(description),
            "criticality": self._assess_criticality(description),
            "scale": self._extract_scale(description),
            "operational_tempo": self._extract_tempo(description)
        }
        
        return context
    
    def _identify_domain(self, description: str) -> str:
        """Identify the operational domain"""
        domains = {
            "banking": ["bank", "financial", "payment", "transaction"],
            "healthcare": ["medical", "health", "patient", "clinical"],
            "transportation": ["vehicle", "traffic", "transport", "autonomous"],
            "defense": ["military", "defense", "weapon", "classified"],
            "energy": ["power", "grid", "nuclear", "utility"],
            "manufacturing": ["factory", "production", "industrial", "scada"]
        }
        
        desc_lower = description.lower()
        for domain, keywords in domains.items():
            if any(keyword in desc_lower for keyword in keywords):
                return domain
                
        return "general_systems"
    
    def _assess_criticality(self, description: str) -> str:
        """Assess mission criticality"""
        critical_indicators = ["life", "safety", "financial", "national", "critical", "essential"]
        desc_lower = description.lower()
        
        if any(indicator in desc_lower for indicator in critical_indicators):
            return "mission_critical"
        return "business_critical"
    
    def _extract_scale(self, description: str) -> Dict[str, str]:
        """Extract operational scale"""
        scale = {
            "geographic": "unknown",
            "users": "unknown",
            "volume": "unknown"
        }
        
        # Geographic scale
        if any(word in description.lower() for word in ["global", "worldwide", "international"]):
            scale["geographic"] = "global"
        elif any(word in description.lower() for word in ["national", "country"]):
            scale["geographic"] = "national"
        elif any(word in description.lower() for word in ["regional", "state"]):
            scale["geographic"] = "regional"
        
        # User scale
        if "million" in description.lower():
            scale["users"] = "millions"
        elif "thousand" in description.lower():
            scale["users"] = "thousands"
        
        # Volume
        if any(word in description.lower() for word in ["high volume", "high frequency"]):
            scale["volume"] = "high_frequency"
            
        return scale
    
    def _extract_tempo(self, description: str) -> Dict[str, Any]:
        """Extract operational tempo"""
        tempo = {
            "normal": "business_hours",
            "peak_periods": [],
            "critical_dates": []
        }
        
        if "24/7" in description or "24x7" in description:
            tempo["normal"] = "24x7"
        elif "real-time" in description.lower():
            tempo["normal"] = "real_time"
            
        return tempo
    
    async def _extract_operational_constraints(self, description: str) -> Dict[str, Any]:
        """Extract operational constraints"""
        constraints = {
            "regulatory": self._extract_regulatory_constraints(description),
            "business": self._extract_business_constraints(description),
            "organizational": self._extract_organizational_constraints(description)
        }
        
        return constraints
    
    def _extract_regulatory_constraints(self, description: str) -> Dict[str, Any]:
        """Extract regulatory constraints"""
        regulations = []
        
        # Common regulations
        reg_patterns = {
            "PCI-DSS": r"PCI[\s-]?DSS",
            "HIPAA": r"HIPAA",
            "GDPR": r"GDPR",
            "SOX": r"SOX|Sarbanes",
            "NERC-CIP": r"NERC[\s-]?CIP",
            "FISMA": r"FISMA"
        }
        
        for reg_name, pattern in reg_patterns.items():
            if re.search(pattern, description, re.IGNORECASE):
                regulations.append(reg_name)
        
        return {
            "frameworks": regulations,
            "audit_frequency": "periodic",
            "change_approval": "required" if regulations else "standard"
        }
    
    def _extract_business_constraints(self, description: str) -> Dict[str, Any]:
        """Extract business constraints"""
        constraints = {}
        
        # Availability
        sla_match = re.search(r"(\d+\.?\d*)\s*%\s*(?:SLA|availability|uptime)", description, re.IGNORECASE)
        if sla_match:
            constraints["availability_requirement"] = f"{sla_match.group(1)}% SLA"
        
        # Transaction volume
        volume_match = re.search(r"(\d+[MKB]?)\+?\s*(?:transactions?|requests?)/(?:day|hour|minute)", description, re.IGNORECASE)
        if volume_match:
            constraints["transaction_volume"] = volume_match.group(0)
        
        # Legacy requirements
        if "legacy" in description.lower():
            constraints["legacy_integration"] = "required"
            
        return constraints
    
    def _extract_organizational_constraints(self, description: str) -> Dict[str, Any]:
        """Extract organizational constraints"""
        return {
            "risk_appetite": "low",  # Default for critical systems
            "security_maturity": "developing",
            "change_capacity": "moderate"
        }
    
    async def _extract_environmental_assumptions(self, description: str) -> Dict[str, Any]:
        """Extract environmental assumptions"""
        assumptions = {
            "user_behavior": [],
            "threat_landscape": [],
            "infrastructure": [],
            "trust_relationships": []
        }
        
        # User behavior assumptions
        if "untrusted" in description.lower() or "internet" in description.lower():
            assumptions["user_behavior"].append("untrusted_networks")
        if "mobile" in description.lower():
            assumptions["user_behavior"].append("mobile_device_usage")
        
        # Threat assumptions
        if "nation" in description.lower() and "state" in description.lower():
            assumptions["threat_landscape"].append("nation_state_actors")
        if "insider" in description.lower():
            assumptions["threat_landscape"].append("insider_threats")
        if "sophisticated" in description.lower():
            assumptions["threat_landscape"].append("sophisticated_adversaries")
        
        # Infrastructure assumptions
        if "cloud" in description.lower():
            assumptions["infrastructure"].append("cloud_deployment")
        if "hybrid" in description.lower():
            assumptions["infrastructure"].append("hybrid_infrastructure")
        
        return assumptions
    
    def validate_abstraction_level(self, content: str) -> bool:
        """Validate mission-level abstraction"""
        # Check for implementation details
        if self.is_implementation_detail(content):
            return False
        
        # Check for prevention language
        if self.is_prevention_language(content):
            return False
            
        return True