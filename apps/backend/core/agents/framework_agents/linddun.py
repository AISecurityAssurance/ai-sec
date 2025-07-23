"""
LINDDUN Agent Implementation
Privacy threat modeling framework for personal data protection
"""
from typing import List, Dict, Any, Optional
import re
import time
from uuid import uuid4

from core.agents.base import BaseAnalysisAgent, SectionResult
from core.models.schemas import FrameworkType, AgentContext, AgentResult
from core.templates.mapper import TemplateMapper
from core.agents.websocket_integration import AgentWebSocketNotifier


class LinddunAgent(BaseAnalysisAgent):
    """
    LINDDUN Privacy Analysis Agent
    
    Analyzes privacy threats across 7 categories:
    - Linking
    - Identifying
    - Non-repudiation
    - Detecting
    - Data Disclosure
    - Unawareness
    - Non-compliance
    """
    
    def __init__(self):
        super().__init__(FrameworkType.LINDDUN)
        
    async def analyze(
        self, 
        context: AgentContext, 
        section_ids: Optional[List[str]] = None,
        notifier: Optional[AgentWebSocketNotifier] = None
    ) -> AgentResult:
        """Run LINDDUN analysis"""
        start_time = time.time()
        
        # Notify analysis start
        if notifier:
            await notifier.notify_analysis_start("LINDDUN")
        
        sections = await self.analyze_sections(context, section_ids, notifier)
        
        # Calculate token usage (estimate)
        total_tokens = len(context.system_description.split()) * 9  # Privacy analysis is detailed
        
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
            await notifier.notify_analysis_complete("LINDDUN", success, error)
            
        return result
    
    def get_sections(self) -> List[Dict[str, str]]:
        """Return list of sections this agent can analyze"""
        return [
            {"id": "data_mapping", "title": "Personal Data Mapping", "template": "table"},
            {"id": "data_flows", "title": "Data Flow Analysis", "template": "diagram"},
            {"id": "privacy_threats", "title": "Privacy Threats", "template": "table"},
            {"id": "threat_distribution", "title": "Threat Distribution", "template": "chart"},
            {"id": "privacy_controls", "title": "Privacy Controls", "template": "table"},
            {"id": "compliance_assessment", "title": "Compliance Assessment", "template": "table"},
            {"id": "privacy_impact", "title": "Privacy Impact Matrix", "template": "heat_map"},
            {"id": "recommendations", "title": "Privacy Recommendations", "template": "section"}
        ]
    
    async def _parse_response(self, response: str, section_id: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        mapper = TemplateMapper()
        
        if section_id == "data_mapping":
            data_elements = self._parse_data_mapping(response)
            return mapper.map_to_table(
                headers=["Component", "Data Types", "Purpose", "Legal Basis", "Retention"],
                rows=[[
                    elem["component"],
                    ", ".join(elem["data_types"]),
                    elem["purpose"],
                    elem["legal_basis"],
                    elem["retention"]
                ] for elem in data_elements]
            )
            
        elif section_id == "data_flows":
            flows = self._parse_data_flows(response)
            return mapper.map_to_flow_diagram(
                nodes=flows["nodes"],
                edges=flows["edges"],
                layout="hierarchical"
            )
            
        elif section_id == "privacy_threats":
            threats = self._parse_privacy_threats(response)
            return mapper.map_to_table(
                headers=["ID", "Category", "Component", "Threat", "Impact", "Likelihood", "Status"],
                rows=[[
                    threat["id"],
                    threat["category"],
                    threat["component"],
                    threat["description"],
                    threat["impact"],
                    threat["likelihood"],
                    threat.get("status", "identified")
                ] for threat in threats]
            )
            
        elif section_id == "threat_distribution":
            threats = self._parse_privacy_threats(response)
            return self._create_threat_distribution(threats, mapper)
            
        elif section_id == "privacy_controls":
            controls = self._parse_privacy_controls(response)
            return mapper.map_to_table(
                headers=["ID", "Control", "Type", "Description", "Effectiveness"],
                rows=[[
                    control["id"],
                    control["name"],
                    control["type"],
                    control["description"],
                    control["effectiveness"]
                ] for control in controls]
            )
            
        elif section_id == "compliance_assessment":
            compliance = self._parse_compliance(response)
            return mapper.map_to_table(
                headers=["Requirement", "Status", "Evidence", "Gaps"],
                rows=[[
                    comp["requirement"],
                    comp["status"],
                    comp["evidence"],
                    comp.get("gaps", "None")
                ] for comp in compliance]
            )
            
        elif section_id == "privacy_impact":
            threats = self._parse_privacy_threats(response)
            return self._create_privacy_impact_matrix(threats, mapper)
            
        elif section_id == "recommendations":
            return self._parse_recommendations(response)
            
        else:
            return mapper.map_to_text(response, "markdown")
    
    def _parse_data_mapping(self, response: str) -> List[Dict[str, Any]]:
        """Parse personal data mapping from response"""
        data_elements = []
        
        # Look for element sections
        element_pattern = r"ELEMENT:\s*(.+?)(?:Data Types:|$)"
        
        # Split response by elements
        element_sections = re.split(r"(?=ELEMENT:)", response, flags=re.IGNORECASE)
        
        for section in element_sections:
            if not section.strip():
                continue
                
            # Extract component name
            comp_match = re.search(element_pattern, section, re.IGNORECASE | re.MULTILINE)
            if not comp_match:
                continue
                
            component = comp_match.group(1).strip()
            
            # Extract data types
            types_match = re.search(r"Data Types:\s*(.+?)(?:Processing Purpose:|$)", section, re.IGNORECASE | re.DOTALL)
            data_types = []
            if types_match:
                types_text = types_match.group(1)
                data_types = [t.strip() for t in re.findall(r"[-]\s*(.+?)(?:\n|$)", types_text)]
                
            # Extract purpose
            purpose_match = re.search(r"Processing Purpose:\s*(.+?)(?:Legal Basis:|$)", section, re.IGNORECASE)
            purpose = purpose_match.group(1).strip() if purpose_match else "Not specified"
            
            # Extract legal basis
            legal_match = re.search(r"Legal Basis:\s*(.+?)(?:\n|LINDDUN|$)", section, re.IGNORECASE)
            legal_basis = legal_match.group(1).strip() if legal_match else "Consent"
            
            # Extract retention
            retention_match = re.search(r"Retention.*?:\s*(.+?)(?:\n|$)", section, re.IGNORECASE)
            retention = retention_match.group(1).strip() if retention_match else "As per policy"
            
            data_elements.append({
                "component": component,
                "data_types": data_types,
                "purpose": purpose,
                "legal_basis": legal_basis,
                "retention": retention
            })
            
        return data_elements
    
    def _parse_data_flows(self, response: str) -> Dict[str, Any]:
        """Parse data flows into diagram format"""
        nodes = []
        edges = []
        node_map = {}
        
        # Extract data flow patterns
        flow_pattern = r"(.+?)\s*(?:�|->|flows to|sends)\s*(.+?)(?:\n|$)"
        
        for match in re.finditer(flow_pattern, response, re.MULTILINE):
            source = match.group(1).strip()
            target = match.group(2).strip()
            
            # Create nodes if not exists
            if source not in node_map:
                node_id = f"node_{len(nodes)}"
                nodes.append({
                    "id": node_id,
                    "label": source,
                    "type": self._classify_node_type(source)
                })
                node_map[source] = node_id
                
            if target not in node_map:
                node_id = f"node_{len(nodes)}"
                nodes.append({
                    "id": node_id,
                    "label": target,
                    "type": self._classify_node_type(target)
                })
                node_map[target] = node_id
                
            # Create edge
            edges.append({
                "id": f"edge_{len(edges)}",
                "source": node_map[source],
                "target": node_map[target],
                "label": "personal data",
                "type": "data_flow"
            })
            
        return {"nodes": nodes, "edges": edges}
    
    def _parse_privacy_threats(self, response: str) -> List[Dict[str, Any]]:
        """Parse LINDDUN privacy threats from response"""
        threats = []
        
        # Categories
        categories = {
            'L': 'Linking',
            'I': 'Identifying', 
            'N': 'Non-repudiation',
            'D': 'Detecting',
            'D2': 'Data Disclosure',
            'U': 'Unawareness',
            'N2': 'Non-compliance'
        }
        
        # Look for category sections
        for cat_letter, cat_name in categories.items():
            # Find category section
            if cat_letter in ['D2', 'N2']:
                # Handle second D and N
                pattern = rf"{cat_letter[0]}.*?-.*?{cat_name}:(.*?)(?:[LINDUN]\s*-|PRIVACY CONTROLS|$)"
            else:
                pattern = rf"{cat_letter}\s*-\s*{cat_name}:(.*?)(?:[LINDUN]\s*-|PRIVACY CONTROLS|$)"
                
            cat_match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
            if cat_match:
                cat_content = cat_match.group(1)
                
                # Parse individual threats
                threat_pattern = rf"{cat_letter}\d+:\s*(.+?)(?:Scenario:|Impact:|{cat_letter}\d+:|$)"
                for threat_match in re.finditer(threat_pattern, cat_content, re.DOTALL):
                    threat_desc = threat_match.group(1).strip()
                    
                    # Extract details
                    details_text = cat_content[threat_match.start():]
                    
                    # Scenario
                    scenario_match = re.search(r"Scenario:\s*(.+?)(?:Impact:|Control:|$)", details_text, re.IGNORECASE | re.DOTALL)
                    
                    # Impact
                    impact_match = re.search(r"Impact:\s*(.+?)(?:Control:|$)", details_text, re.IGNORECASE | re.DOTALL)
                    impact_text = impact_match.group(1).strip() if impact_match else ""
                    
                    # Assess impact and likelihood
                    impact_level = self._assess_privacy_impact(impact_text)
                    likelihood = self._assess_threat_likelihood(threat_desc)
                    
                    threats.append({
                        "id": f"LIN-{len(threats)+1:03d}",
                        "category": cat_name,
                        "component": self._extract_component(threat_desc),
                        "description": threat_desc,
                        "impact": impact_level,
                        "likelihood": likelihood,
                        "status": "identified"
                    })
                    
        return threats
    
    def _parse_privacy_controls(self, response: str) -> List[Dict[str, Any]]:
        """Parse privacy controls from response"""
        controls = []
        
        # Look for privacy controls section
        controls_section = re.search(r"PRIVACY CONTROLS:(.*?)(?:COMPLIANCE CHECK|$)", response, re.IGNORECASE | re.DOTALL)
        
        if controls_section:
            content = controls_section.group(1)
            
            # Parse technical controls
            tech_section = re.search(r"Technical:(.*?)(?:Organizational:|$)", content, re.IGNORECASE | re.DOTALL)
            if tech_section:
                tech_content = tech_section.group(1)
                control_items = re.findall(r"(?:[-]|\d+\.)\s*(.+?):\s*(.+?)(?:\n|$)", tech_content, re.MULTILINE)
                
                for name, desc in control_items:
                    controls.append({
                        "id": f"PC-{len(controls)+1:03d}",
                        "name": name.strip(),
                        "type": "Technical",
                        "description": desc.strip(),
                        "effectiveness": self._assess_control_effectiveness(desc)
                    })
                    
            # Parse organizational controls
            org_section = re.search(r"Organizational:(.*?)(?:COMPLIANCE|$)", content, re.IGNORECASE | re.DOTALL)
            if org_section:
                org_content = org_section.group(1)
                control_items = re.findall(r"(?:[-]|\d+\.)\s*(.+?):\s*(.+?)(?:\n|$)", org_content, re.MULTILINE)
                
                for name, desc in control_items:
                    controls.append({
                        "id": f"PC-{len(controls)+1:03d}",
                        "name": name.strip(),
                        "type": "Organizational",
                        "description": desc.strip(),
                        "effectiveness": self._assess_control_effectiveness(desc)
                    })
                    
        return controls
    
    def _parse_compliance(self, response: str) -> List[Dict[str, Any]]:
        """Parse compliance assessment from response"""
        compliance_items = []
        
        # Look for compliance check section
        comp_section = re.search(r"COMPLIANCE CHECK:(.*?)$", response, re.IGNORECASE | re.DOTALL)
        
        if comp_section:
            content = comp_section.group(1)
            
            # GDPR principles
            principles = [
                "Lawfulness", "Purpose Limitation", "Data Minimization",
                "Accuracy", "Storage Limitation", "Integrity", "Accountability"
            ]
            
            for principle in principles:
                # Look for principle assessment
                prin_match = re.search(rf"{principle}:\s*([])\s*(.+?)(?:\n|$)", content, re.IGNORECASE)
                if prin_match:
                    status = "Compliant" if prin_match.group(1) == "" else "Non-compliant"
                    explanation = prin_match.group(2).strip()
                    
                    compliance_items.append({
                        "requirement": f"GDPR - {principle}",
                        "status": status,
                        "evidence": explanation,
                        "gaps": "None" if status == "Compliant" else "Remediation required"
                    })
                    
            # Look for other regulations
            if "CCPA" in content.upper():
                compliance_items.append({
                    "requirement": "CCPA - Consumer Rights",
                    "status": "Partial",
                    "evidence": "Rights request process in place",
                    "gaps": "Automated fulfillment needed"
                })
                
        return compliance_items
    
    def _parse_recommendations(self, response: str) -> Dict[str, Any]:
        """Parse privacy recommendations"""
        content = "## Privacy Enhancement Recommendations\n\n"
        
        # Look for recommendations in response
        rec_section = re.search(r"(?:RECOMMENDATIONS?|PRIVACY CONTROLS):(.*?)$", response, re.IGNORECASE | re.DOTALL)
        
        if rec_section:
            rec_content = rec_section.group(1)
            
            # Extract priority recommendations
            high_priority = re.findall(r"(?:High Priority|Critical|Immediate).*?:\s*(.+?)(?:\n|$)", rec_content, re.IGNORECASE)
            if high_priority:
                content += "### High Priority Actions\n"
                for rec in high_priority:
                    content += f"- {rec.strip()}\n"
                content += "\n"
                
            # Extract medium priority
            med_priority = re.findall(r"(?:Medium Priority|Important).*?:\s*(.+?)(?:\n|$)", rec_content, re.IGNORECASE)
            if med_priority:
                content += "### Medium Priority Actions\n"
                for rec in med_priority:
                    content += f"- {rec.strip()}\n"
                content += "\n"
                    
        # Add standard privacy recommendations
        content += """### Privacy by Design Principles
- Implement data minimization across all processes
- Use privacy-preserving techniques (anonymization, pseudonymization)
- Enhance user transparency and control
- Regular privacy impact assessments
- Privacy-aware system architecture
- Strong consent management
- Rights fulfillment automation
"""
        
        mapper = TemplateMapper()
        return mapper.map_to_text(content, "markdown")
    
    def _create_threat_distribution(self, threats: List[Dict[str, Any]], mapper: TemplateMapper) -> Dict[str, Any]:
        """Create threat distribution chart"""
        # Count threats by category
        category_counts = {}
        for threat in threats:
            cat = threat["category"]
            category_counts[cat] = category_counts.get(cat, 0) + 1
            
        return mapper.map_to_chart(
            chart_type="doughnut",
            data={
                "labels": list(category_counts.keys()),
                "values": list(category_counts.values()),
                "colors": ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40", "#FF6384"]
            },
            title="Privacy Threats by LINDDUN Category"
        )
    
    def _create_privacy_impact_matrix(self, threats: List[Dict[str, Any]], mapper: TemplateMapper) -> Dict[str, Any]:
        """Create privacy impact assessment matrix"""
        # Initialize matrix
        matrix = {
            "low": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "medium": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "high": {"low": 0, "medium": 0, "high": 0, "critical": 0}
        }
        
        # Populate matrix
        for threat in threats:
            likelihood = threat.get("likelihood", "medium")
            impact = threat.get("impact", "medium")
            
            if likelihood in matrix and impact in ["low", "medium", "high", "critical"]:
                matrix[likelihood][impact] += 1
                
        # Convert to heat map format
        return mapper.map_to_heat_map(
            x_labels=["Low Impact", "Medium Impact", "High Impact", "Critical Impact"],
            y_labels=["High Likelihood", "Medium Likelihood", "Low Likelihood"],
            data=[
                [matrix["high"]["low"], matrix["high"]["medium"], matrix["high"]["high"], matrix["high"]["critical"]],
                [matrix["medium"]["low"], matrix["medium"]["medium"], matrix["medium"]["high"], matrix["medium"]["critical"]],
                [matrix["low"]["low"], matrix["low"]["medium"], matrix["low"]["high"], matrix["low"]["critical"]]
            ],
            title="Privacy Risk Matrix"
        )
    
    def _classify_node_type(self, name: str) -> str:
        """Classify node type for data flow diagram"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ["user", "customer", "employee"]):
            return "data_subject"
        elif any(word in name_lower for word in ["database", "storage", "repository"]):
            return "data_store"
        elif any(word in name_lower for word in ["system", "service", "application"]):
            return "process"
        elif any(word in name_lower for word in ["third", "external", "partner"]):
            return "external_entity"
        else:
            return "component"
            
    def _extract_component(self, text: str) -> str:
        """Extract component name from threat description"""
        # Look for common patterns
        comp_match = re.search(r"(?:in|at|from|of)\s+(?:the\s+)?(\w+(?:\s+\w+)?)\s*(?:system|service|component|database)", text, re.IGNORECASE)
        if comp_match:
            return comp_match.group(1).strip()
            
        # Default to first few words
        words = text.split()[:3]
        return " ".join(words)
        
    def _assess_privacy_impact(self, text: str) -> str:
        """Assess privacy impact level"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["critical", "severe", "mass", "all users"]):
            return "critical"
        elif any(word in text_lower for word in ["high", "significant", "many users"]):
            return "high"
        elif any(word in text_lower for word in ["low", "minimal", "few users"]):
            return "low"
        else:
            return "medium"
            
    def _assess_threat_likelihood(self, text: str) -> str:
        """Assess threat likelihood"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["easy", "common", "frequent"]):
            return "high"
        elif any(word in text_lower for word in ["difficult", "rare", "unlikely"]):
            return "low"
        else:
            return "medium"
            
    def _assess_control_effectiveness(self, desc: str) -> str:
        """Assess control effectiveness"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["strong", "comprehensive", "complete"]):
            return "High"
        elif any(word in desc_lower for word in ["basic", "partial", "limited"]):
            return "Low"
        else:
            return "Medium"
    
    def _extract_artifacts(self, sections: List[SectionResult]) -> List[Dict[str, Any]]:
        """Extract key artifacts for other agents to use"""
        artifacts = []
        
        for section in sections:
            if section.section_id == "data_mapping" and section.status.value == "completed":
                artifacts.append({
                    "type": "personal_data_inventory",
                    "name": "LINDDUN Personal Data Map",
                    "data": section.content
                })
            elif section.section_id == "privacy_threats" and section.status.value == "completed":
                artifacts.append({
                    "type": "privacy_threats",
                    "name": "LINDDUN Privacy Threats",
                    "data": section.content
                })
            elif section.section_id == "compliance_assessment" and section.status.value == "completed":
                artifacts.append({
                    "type": "compliance_status",
                    "name": "LINDDUN Compliance Assessment",
                    "data": section.content
                })
                
        return artifacts