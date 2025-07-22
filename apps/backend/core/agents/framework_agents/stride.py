"""
STRIDE Agent Implementation
Systematic threat identification across six categories
"""
from typing import List, Dict, Any, Optional
import re
import time
from uuid import uuid4

from core.agents.base import BaseAnalysisAgent, SectionResult
from core.models.schemas import FrameworkType, AgentContext, AgentResult
from core.templates.mapper import TemplateMapper
from core.agents.websocket_integration import AgentWebSocketNotifier


class StrideAgent(BaseAnalysisAgent):
    """
    STRIDE Threat Modeling Agent
    
    Analyzes system for:
    - Spoofing
    - Tampering
    - Repudiation
    - Information Disclosure
    - Denial of Service
    - Elevation of Privilege
    """
    
    def __init__(self):
        super().__init__(FrameworkType.STRIDE)
        
    async def analyze(
        self, 
        context: AgentContext, 
        section_ids: Optional[List[str]] = None,
        notifier: Optional[AgentWebSocketNotifier] = None
    ) -> AgentResult:
        """Run STRIDE analysis"""
        start_time = time.time()
        
        # Notify analysis start
        if notifier:
            await notifier.notify_analysis_start("STRIDE")
        
        sections = await self.analyze_sections(context, section_ids, notifier)
        
        # Calculate token usage (estimate)
        total_tokens = len(context.system_description.split()) * 8  # Rough estimate
        
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
            await notifier.notify_analysis_complete("STRIDE", success, error)
            
        return result
    
    def get_sections(self) -> List[Dict[str, str]]:
        """Return list of sections this agent can analyze"""
        return [
            {"id": "overview", "title": "STRIDE Overview", "template": "chart"},
            {"id": "threats", "title": "Identified Threats", "template": "table"},
            {"id": "by_category", "title": "Threats by Category", "template": "chart"},
            {"id": "by_component", "title": "Threats by Component", "template": "table"},
            {"id": "mitigations", "title": "Recommended Mitigations", "template": "table"},
            {"id": "risk_matrix", "title": "Risk Assessment Matrix", "template": "heat_map"}
        ]
    
    async def _parse_response(self, response: str, section_id: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        mapper = TemplateMapper()
        
        if section_id == "overview":
            return self._parse_overview(response)
            
        elif section_id == "threats":
            threats = self._parse_threats(response)
            return mapper.map_to_table(
                headers=["ID", "Component", "Type", "Description", "Risk Level", "Status"],
                rows=[[
                    threat["id"],
                    threat["component"],
                    threat["threat_type"],
                    threat["description"],
                    threat["risk_level"],
                    threat.get("status", "identified")
                ] for threat in threats]
            )
            
        elif section_id == "by_category":
            threats = self._parse_threats(response)
            category_counts = {}
            for threat in threats:
                cat = threat["threat_type"]
                category_counts[cat] = category_counts.get(cat, 0) + 1
                
            return mapper.map_to_chart(
                chart_type="bar",
                data={
                    "labels": list(category_counts.keys()),
                    "values": list(category_counts.values())
                },
                title="Threats by STRIDE Category",
                x_label="Category",
                y_label="Count"
            )
            
        elif section_id == "by_component":
            threats = self._parse_threats(response)
            component_threats = {}
            for threat in threats:
                comp = threat["component"]
                if comp not in component_threats:
                    component_threats[comp] = []
                component_threats[comp].append(threat)
                
            rows = []
            for component, comp_threats in component_threats.items():
                threat_summary = ", ".join([t["threat_type"][0] for t in comp_threats])
                critical_count = sum(1 for t in comp_threats if t["risk_level"] == "critical")
                high_count = sum(1 for t in comp_threats if t["risk_level"] == "high")
                
                rows.append([
                    component,
                    len(comp_threats),
                    threat_summary,
                    f"Critical: {critical_count}, High: {high_count}"
                ])
                
            return mapper.map_to_table(
                headers=["Component", "Threat Count", "Types", "Risk Summary"],
                rows=rows
            )
            
        elif section_id == "mitigations":
            mitigations = self._parse_mitigations(response)
            return mapper.map_to_table(
                headers=["Threat ID", "Mitigation", "Priority", "Implementation"],
                rows=[[
                    mit["threat_id"],
                    mit["description"],
                    mit["priority"],
                    mit.get("implementation", "Proposed")
                ] for mit in mitigations]
            )
            
        elif section_id == "risk_matrix":
            threats = self._parse_threats(response)
            return self._create_risk_matrix(threats, mapper)
            
        else:
            return mapper.map_to_text(response, "markdown")
    
    def _parse_threats(self, response: str) -> List[Dict[str, Any]]:
        """Parse threats from response"""
        threats = []
        
        # Pattern to match threat entries
        # Looking for patterns like "STR-001:" or "S1:" or "Element: Component"
        element_pattern = r"ELEMENT:\s*(.+?)(?:\n|$)"
        threat_pattern = r"(STR-\d+|[STRIDE]\d+):\s*(.+?)(?=STR-\d+:|[STRIDE]\d+:|ELEMENT:|$)"
        
        current_component = "System"
        
        # First, find all elements/components
        for match in re.finditer(element_pattern, response, re.IGNORECASE | re.MULTILINE):
            current_component = match.group(1).strip()
            
            # Find threats for this component
            component_section = response[match.start():]
            next_element = re.search(r"\nELEMENT:", component_section[match.end():])
            if next_element:
                component_section = component_section[:next_element.start() + match.end()]
                
            # Parse threat categories
            for category in ['S', 'T', 'R', 'I', 'D', 'E']:
                category_name = self._get_category_name(category)
                category_pattern = rf"{category}\s*-\s*{category_name}.*?:(.*?)(?=[STRIDE]\s*-|$)"
                
                cat_match = re.search(category_pattern, component_section, re.IGNORECASE | re.DOTALL)
                if cat_match:
                    threats_text = cat_match.group(1)
                    
                    # Parse individual threats
                    threat_item_pattern = rf"{category}\d+:\s*(.+?)(?:Impact:|Mitigation:|{category}\d+:|$)"
                    for threat_match in re.finditer(threat_item_pattern, threats_text, re.DOTALL):
                        threat_desc = threat_match.group(1).strip()
                        
                        # Extract impact and risk level
                        impact_match = re.search(r"Impact:\s*(.+?)(?:Mitigation:|$)", 
                                               threats_text[threat_match.start():], re.DOTALL)
                        impact = impact_match.group(1).strip() if impact_match else ""
                        
                        # Determine risk level based on keywords
                        risk_level = self._assess_risk_level(threat_desc + " " + impact)
                        
                        threats.append({
                            "id": f"STR-{len(threats)+1:03d}",
                            "component": current_component,
                            "threat_type": category_name,
                            "description": threat_desc,
                            "impact": impact,
                            "risk_level": risk_level,
                            "likelihood": self._assess_likelihood(threat_desc),
                            "impact_level": self._assess_impact(impact)
                        })
        
        return threats
    
    def _parse_mitigations(self, response: str) -> List[Dict[str, Any]]:
        """Parse mitigations from response"""
        mitigations = []
        
        # Look for mitigation patterns
        mit_pattern = r"Mitigation:\s*(.+?)(?=STR-\d+:|[STRIDE]\d+:|Mitigation:|ELEMENT:|$)"
        
        for match in re.finditer(mit_pattern, response, re.DOTALL):
            mitigation_text = match.group(1).strip()
            
            # Try to find associated threat ID
            # Look backwards for threat ID
            before_text = response[:match.start()]
            threat_id_match = re.search(r"(STR-\d+|[STRIDE]\d+):", before_text[::-1])
            threat_id = threat_id_match.group(1)[::-1] if threat_id_match else f"STR-{len(mitigations)+1:03d}"
            
            # Assess priority based on keywords
            priority = self._assess_priority(mitigation_text)
            
            mitigations.append({
                "threat_id": threat_id,
                "description": mitigation_text,
                "priority": priority,
                "implementation": "Proposed"
            })
            
        return mitigations
    
    def _parse_overview(self, response: str) -> Dict[str, Any]:
        """Parse overview statistics"""
        threats = self._parse_threats(response)
        
        # Count by risk level
        risk_counts = {
            "critical": sum(1 for t in threats if t["risk_level"] == "critical"),
            "high": sum(1 for t in threats if t["risk_level"] == "high"),
            "medium": sum(1 for t in threats if t["risk_level"] == "medium"),
            "low": sum(1 for t in threats if t["risk_level"] == "low")
        }
        
        # Count by category
        category_counts = {}
        for threat in threats:
            cat = threat["threat_type"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
        mapper = TemplateMapper()
        return mapper.map_to_chart(
            chart_type="doughnut",
            data={
                "labels": ["Critical", "High", "Medium", "Low"],
                "values": [risk_counts["critical"], risk_counts["high"], 
                          risk_counts["medium"], risk_counts["low"]],
                "colors": ["#dc2626", "#f59e0b", "#3b82f6", "#10b981"]
            },
            title="Threat Risk Distribution"
        )
    
    def _create_risk_matrix(self, threats: List[Dict[str, Any]], mapper: TemplateMapper) -> Dict[str, Any]:
        """Create risk assessment matrix"""
        # Initialize matrix
        matrix = {
            "low": {"low": 0, "medium": 0, "high": 0},
            "medium": {"low": 0, "medium": 0, "high": 0},
            "high": {"low": 0, "medium": 0, "high": 0}
        }
        
        # Populate matrix
        for threat in threats:
            likelihood = threat.get("likelihood", "medium")
            impact = threat.get("impact_level", "medium")
            if likelihood in matrix and impact in matrix[likelihood]:
                matrix[likelihood][impact] += 1
                
        # Convert to heat map format
        return mapper.map_to_heat_map(
            x_labels=["Low Impact", "Medium Impact", "High Impact"],
            y_labels=["High Likelihood", "Medium Likelihood", "Low Likelihood"],
            data=[
                [matrix["high"]["low"], matrix["high"]["medium"], matrix["high"]["high"]],
                [matrix["medium"]["low"], matrix["medium"]["medium"], matrix["medium"]["high"]],
                [matrix["low"]["low"], matrix["low"]["medium"], matrix["low"]["high"]]
            ],
            title="Risk Assessment Matrix"
        )
    
    def _get_category_name(self, letter: str) -> str:
        """Get full category name from letter"""
        mapping = {
            'S': 'Spoofing',
            'T': 'Tampering',
            'R': 'Repudiation',
            'I': 'Information Disclosure',
            'D': 'Denial of Service',
            'E': 'Elevation of Privilege'
        }
        return mapping.get(letter.upper(), letter)
    
    def _assess_risk_level(self, text: str) -> str:
        """Assess risk level based on text content"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'severe', 'catastrophic', 'complete compromise']):
            return 'critical'
        elif any(word in text_lower for word in ['high', 'significant', 'major', 'serious']):
            return 'high'
        elif any(word in text_lower for word in ['low', 'minor', 'minimal', 'unlikely']):
            return 'low'
        else:
            return 'medium'
    
    def _assess_likelihood(self, text: str) -> str:
        """Assess likelihood based on text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['likely', 'common', 'frequent', 'easy']):
            return 'high'
        elif any(word in text_lower for word in ['unlikely', 'difficult', 'rare', 'complex']):
            return 'low'
        else:
            return 'medium'
            
    def _assess_impact(self, text: str) -> str:
        """Assess impact level based on text"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['catastrophic', 'complete', 'total', 'severe']):
            return 'high'
        elif any(word in text_lower for word in ['minimal', 'minor', 'limited', 'small']):
            return 'low'
        else:
            return 'medium'
            
    def _assess_priority(self, text: str) -> str:
        """Assess mitigation priority"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['immediate', 'critical', 'urgent', 'asap']):
            return 'Critical'
        elif any(word in text_lower for word in ['important', 'should', 'recommend']):
            return 'High'
        elif any(word in text_lower for word in ['consider', 'optional', 'nice to have']):
            return 'Low'
        else:
            return 'Medium'
    
    def _extract_artifacts(self, sections: List[SectionResult]) -> List[Dict[str, Any]]:
        """Extract key artifacts for other agents to use"""
        artifacts = []
        
        for section in sections:
            if section.section_id == "threats" and section.status.value == "completed":
                artifacts.append({
                    "type": "stride_threats",
                    "name": "STRIDE Threat Catalog",
                    "data": section.content
                })
            elif section.section_id == "mitigations" and section.status.value == "completed":
                artifacts.append({
                    "type": "security_controls",
                    "name": "STRIDE Mitigations",
                    "data": section.content
                })
                
        return artifacts