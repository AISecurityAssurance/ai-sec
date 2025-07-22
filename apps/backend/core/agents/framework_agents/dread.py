"""
DREAD Agent Implementation
Risk assessment model for systematic threat prioritization
"""
from typing import List, Dict, Any, Optional
import re
import time
from uuid import uuid4

from core.agents.base import BaseAnalysisAgent, SectionResult
from core.models.schemas import FrameworkType, AgentContext, AgentResult
from core.templates.mapper import TemplateMapper
from core.agents.websocket_integration import AgentWebSocketNotifier


class DreadAgent(BaseAnalysisAgent):
    """
    DREAD Risk Assessment Agent
    
    Scores threats across 5 dimensions:
    - Damage
    - Reproducibility
    - Exploitability
    - Affected Users
    - Discoverability
    """
    
    def __init__(self):
        super().__init__(FrameworkType.DREAD)
        
    async def analyze(
        self, 
        context: AgentContext, 
        section_ids: Optional[List[str]] = None,
        notifier: Optional[AgentWebSocketNotifier] = None
    ) -> AgentResult:
        """Run DREAD analysis"""
        start_time = time.time()
        
        # Notify analysis start
        if notifier:
            await notifier.notify_analysis_start("DREAD")
        
        sections = await self.analyze_sections(context, section_ids, notifier)
        
        # Calculate token usage (estimate)
        total_tokens = len(context.system_description.split()) * 6  # DREAD is focused
        
        result = AgentResult(
            framework=self.framework,
            sections=[s.model_dump() for s in sections],
            artifacts=self._extract_artifacts(sections),
            duration=time.time() - start_time,
            token_usage={
                "input_tokens": total_tokens // 2,
                "output_tokens": total_tokens // 2,
                "total_tokens": total_tokens
            }
        )
        
        # Notify analysis complete
        if notifier:
            success = all(s.status == "completed" for s in sections)
            error = next((s.error for s in sections if s.error), None)
            await notifier.notify_analysis_complete("DREAD", success, error)
            
        return result
    
    def get_sections(self) -> List[Dict[str, str]]:
        """Return list of sections this agent can analyze"""
        return [
            {"id": "overview", "title": "Risk Overview", "template": "chart"},
            {"id": "assessments", "title": "DREAD Assessments", "template": "table"},
            {"id": "by_category", "title": "Risk by Category", "template": "chart"},
            {"id": "distribution", "title": "Score Distribution", "template": "chart"},
            {"id": "priority_matrix", "title": "Priority Matrix", "template": "heat_map"},
            {"id": "recommendations", "title": "Mitigation Recommendations", "template": "table"}
        ]
    
    async def _parse_response(self, response: str, section_id: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        mapper = TemplateMapper()
        
        if section_id == "overview":
            return self._parse_overview(response)
            
        elif section_id == "assessments":
            threats = self._parse_threats(response)
            return mapper.map_to_table(
                headers=["ID", "Threat", "D", "R", "E", "A", "D", "Total", "Risk Level"],
                rows=[[
                    threat["id"],
                    threat["threat"],
                    threat["scores"]["damage"],
                    threat["scores"]["reproducibility"],
                    threat["scores"]["exploitability"],
                    threat["scores"]["affected_users"],
                    threat["scores"]["discoverability"],
                    threat["total_score"],
                    threat["risk_level"]
                ] for threat in threats]
            )
            
        elif section_id == "by_category":
            threats = self._parse_threats(response)
            category_risks = self._aggregate_by_category(threats)
            
            return mapper.map_to_chart(
                chart_type="bar",
                data={
                    "labels": list(category_risks.keys()),
                    "values": list(category_risks.values())
                },
                title="Average Risk Score by Category",
                x_label="Category",
                y_label="Average DREAD Score"
            )
            
        elif section_id == "distribution":
            threats = self._parse_threats(response)
            return self._create_score_distribution(threats, mapper)
            
        elif section_id == "priority_matrix":
            threats = self._parse_threats(response)
            return self._create_priority_matrix(threats, mapper)
            
        elif section_id == "recommendations":
            recommendations = self._parse_recommendations(response)
            return mapper.map_to_table(
                headers=["Priority", "Threat ID", "Mitigation", "Impact", "Effort"],
                rows=[[
                    rec["priority"],
                    rec["threat_id"],
                    rec["mitigation"],
                    rec["impact"],
                    rec["effort"]
                ] for rec in recommendations]
            )
            
        else:
            return mapper.map_to_text(response, "markdown")
    
    def _parse_threats(self, response: str) -> List[Dict[str, Any]]:
        """Parse DREAD threat assessments from response"""
        threats = []
        
        # Pattern to match threat sections
        threat_pattern = r"THREAT:\s*(.+?)(?:Source:|$)"
        
        # Split response into threat sections
        threat_sections = re.split(r"(?=THREAT:)", response, flags=re.IGNORECASE)
        
        for section in threat_sections:
            if not section.strip():
                continue
                
            # Extract threat description
            threat_match = re.search(threat_pattern, section, re.IGNORECASE | re.MULTILINE)
            if not threat_match:
                continue
                
            threat_desc = threat_match.group(1).strip()
            
            # Extract scores
            scores = {}
            
            # Damage
            damage_match = re.search(r"Damage.*?[:\s]+(\d)", section, re.IGNORECASE)
            scores["damage"] = int(damage_match.group(1)) if damage_match else 2
            
            # Reproducibility
            repro_match = re.search(r"Reproducibility.*?[:\s]+(\d)", section, re.IGNORECASE)
            scores["reproducibility"] = int(repro_match.group(1)) if repro_match else 2
            
            # Exploitability
            exploit_match = re.search(r"Exploitability.*?[:\s]+(\d)", section, re.IGNORECASE)
            scores["exploitability"] = int(exploit_match.group(1)) if exploit_match else 2
            
            # Affected Users
            affected_match = re.search(r"Affected Users.*?[:\s]+(\d)", section, re.IGNORECASE)
            scores["affected_users"] = int(affected_match.group(1)) if affected_match else 2
            
            # Discoverability
            discover_match = re.search(r"Discoverability.*?[:\s]+(\d)", section, re.IGNORECASE)
            scores["discoverability"] = int(discover_match.group(1)) if discover_match else 2
            
            # Calculate total score
            total_score = sum(scores.values())
            
            # Determine risk level
            risk_level = self._get_risk_level(total_score)
            
            # Extract category (from threat description or source)
            category = self._extract_category(threat_desc, section)
            
            threats.append({
                "id": f"DT-{len(threats)+1:03d}",
                "threat": threat_desc,
                "category": category,
                "scores": scores,
                "total_score": total_score,
                "risk_level": risk_level,
                "asset": self._extract_asset(section)
            })
            
        return threats
    
    def _parse_recommendations(self, response: str) -> List[Dict[str, Any]]:
        """Parse mitigation recommendations from response"""
        recommendations = []
        
        # Look for mitigation sections
        mit_pattern = r"MITIGATION.*?:\s*(.+?)(?:Priority:|Based on|$)"
        
        for match in re.finditer(mit_pattern, response, re.IGNORECASE | re.DOTALL):
            mitigation_text = match.group(1).strip()
            
            # Extract priority
            priority_match = re.search(r"Priority:\s*(\w+)", response[match.start():], re.IGNORECASE)
            priority = priority_match.group(1) if priority_match else "Medium"
            
            # Try to find associated threat
            threat_id = self._find_associated_threat_id(response[:match.start()])
            
            # Assess impact and effort
            impact = self._assess_mitigation_impact(mitigation_text)
            effort = self._assess_implementation_effort(mitigation_text)
            
            recommendations.append({
                "priority": priority,
                "threat_id": threat_id,
                "mitigation": mitigation_text,
                "impact": impact,
                "effort": effort
            })
            
        return recommendations
    
    def _parse_overview(self, response: str) -> Dict[str, Any]:
        """Parse risk overview"""
        threats = self._parse_threats(response)
        
        # Count by risk level
        risk_counts = {
            "Critical": sum(1 for t in threats if t["risk_level"] == "Critical"),
            "High": sum(1 for t in threats if t["risk_level"] == "High"),
            "Medium": sum(1 for t in threats if t["risk_level"] == "Medium"),
            "Low": sum(1 for t in threats if t["risk_level"] == "Low")
        }
        
        mapper = TemplateMapper()
        return mapper.map_to_chart(
            chart_type="doughnut",
            data={
                "labels": list(risk_counts.keys()),
                "values": list(risk_counts.values()),
                "colors": ["#8b0000", "#dc143c", "#ff8c00", "#32cd32"]
            },
            title="Risk Level Distribution"
        )
    
    def _create_score_distribution(self, threats: List[Dict[str, Any]], mapper: TemplateMapper) -> Dict[str, Any]:
        """Create score distribution chart"""
        # Aggregate scores by category
        categories = ["damage", "reproducibility", "exploitability", "affected_users", "discoverability"]
        datasets = []
        
        for category in categories:
            scores = [threat["scores"][category] for threat in threats]
            avg_score = sum(scores) / len(scores) if scores else 0
            datasets.append({
                "label": category.replace("_", " ").title(),
                "value": round(avg_score, 2)
            })
            
        return mapper.map_to_chart(
            chart_type="radar",
            data={
                "labels": [d["label"] for d in datasets],
                "values": [d["value"] for d in datasets]
            },
            title="Average DREAD Scores Distribution"
        )
    
    def _create_priority_matrix(self, threats: List[Dict[str, Any]], mapper: TemplateMapper) -> Dict[str, Any]:
        """Create priority matrix based on damage vs exploitability"""
        # Initialize 3x3 matrix
        matrix = [[0 for _ in range(3)] for _ in range(3)]
        
        # Populate matrix
        for threat in threats:
            damage = threat["scores"]["damage"] - 1  # Convert to 0-2 index
            exploit = threat["scores"]["exploitability"] - 1  # Convert to 0-2 index
            matrix[2-exploit][damage] += 1  # Invert Y for display
            
        return mapper.map_to_heat_map(
            x_labels=["Low Damage", "Medium Damage", "High Damage"],
            y_labels=["High Exploitability", "Medium Exploitability", "Low Exploitability"],
            data=matrix,
            title="Priority Matrix (Damage vs Exploitability)"
        )
    
    def _aggregate_by_category(self, threats: List[Dict[str, Any]]) -> Dict[str, float]:
        """Aggregate average risk scores by category"""
        category_scores = {}
        category_counts = {}
        
        for threat in threats:
            category = threat["category"]
            if category not in category_scores:
                category_scores[category] = 0
                category_counts[category] = 0
                
            category_scores[category] += threat["total_score"]
            category_counts[category] += 1
            
        # Calculate averages
        return {
            cat: round(category_scores[cat] / category_counts[cat], 1)
            for cat in category_scores
        }
    
    def _get_risk_level(self, score: int) -> str:
        """Determine risk level based on total score"""
        if score <= 6:
            return "Low"
        elif score <= 9:
            return "Medium"
        elif score <= 12:
            return "High"
        else:
            return "Critical"
            
    def _extract_category(self, threat: str, section: str) -> str:
        """Extract or determine threat category"""
        threat_lower = threat.lower()
        
        # Common categories
        if any(word in threat_lower for word in ['injection', 'validation', 'input']):
            return "Input Validation"
        elif any(word in threat_lower for word in ['authentication', 'login', 'credential']):
            return "Authentication"
        elif any(word in threat_lower for word in ['authorization', 'access control', 'permission']):
            return "Authorization"
        elif any(word in threat_lower for word in ['encryption', 'crypto', 'tls', 'ssl']):
            return "Cryptography"
        elif any(word in threat_lower for word in ['session', 'cookie', 'token']):
            return "Session Management"
        elif any(word in threat_lower for word in ['configuration', 'misconfiguration', 'setting']):
            return "Configuration"
        elif any(word in threat_lower for word in ['dos', 'denial', 'availability']):
            return "Availability"
        else:
            return "General Security"
            
    def _extract_asset(self, section: str) -> str:
        """Extract affected asset from section"""
        asset_match = re.search(r"Asset:\s*(.+?)(?:\n|$)", section, re.IGNORECASE)
        if asset_match:
            return asset_match.group(1).strip()
            
        # Try to extract from threat description
        component_match = re.search(r"(?:in|on|of)\s+(\w+\s*\w*)\s*(?:service|system|component)", section, re.IGNORECASE)
        if component_match:
            return component_match.group(1).strip()
            
        return "System"
        
    def _find_associated_threat_id(self, text: str) -> str:
        """Find threat ID associated with mitigation"""
        # Look for most recent threat ID
        threat_id_match = re.search(r"(DT-\d{3})", text[::-1])
        if threat_id_match:
            return threat_id_match.group(1)[::-1]
            
        return "DT-001"
        
    def _assess_mitigation_impact(self, mitigation: str) -> str:
        """Assess the impact of a mitigation"""
        mit_lower = mitigation.lower()
        
        if any(word in mit_lower for word in ['eliminate', 'prevent', 'block']):
            return "High"
        elif any(word in mit_lower for word in ['reduce', 'minimize', 'limit']):
            return "Medium"
        else:
            return "Low"
            
    def _assess_implementation_effort(self, mitigation: str) -> str:
        """Assess implementation effort for mitigation"""
        mit_lower = mitigation.lower()
        
        if any(word in mit_lower for word in ['redesign', 'rewrite', 'major', 'significant']):
            return "High"
        elif any(word in mit_lower for word in ['simple', 'configuration', 'update', 'patch']):
            return "Low"
        else:
            return "Medium"
    
    def _extract_artifacts(self, sections: List[SectionResult]) -> List[Dict[str, Any]]:
        """Extract key artifacts for other agents to use"""
        artifacts = []
        
        for section in sections:
            if section.section_id == "assessments" and section.status.value == "completed":
                artifacts.append({
                    "type": "dread_scores",
                    "name": "DREAD Risk Assessments",
                    "data": section.content
                })
            elif section.section_id == "recommendations" and section.status.value == "completed":
                artifacts.append({
                    "type": "mitigation_priorities",
                    "name": "DREAD Mitigation Priorities",
                    "data": section.content
                })
                
        return artifacts