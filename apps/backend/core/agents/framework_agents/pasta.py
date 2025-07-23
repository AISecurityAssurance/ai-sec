"""
PASTA Agent Implementation
Process for Attack Simulation and Threat Analysis - 7-stage risk-centric methodology
"""
from typing import List, Dict, Any, Optional
import re
import time
from uuid import uuid4

from core.agents.base import BaseAnalysisAgent, SectionResult
from core.models.schemas import FrameworkType, AgentContext, AgentResult
from core.templates.mapper import TemplateMapper
from core.agents.websocket_integration import AgentWebSocketNotifier


class PastaAgent(BaseAnalysisAgent):
    """
    PASTA (Process for Attack Simulation and Threat Analysis) Agent
    
    Implements 7-stage methodology:
    1. Define Objectives
    2. Define Technical Scope  
    3. Application Decomposition
    4. Threat Analysis
    5. Vulnerability & Weakness Analysis
    6. Attack Modeling
    7. Risk & Impact Analysis
    """
    
    def __init__(self):
        super().__init__(FrameworkType.PASTA)
        
    async def analyze(
        self, 
        context: AgentContext, 
        section_ids: Optional[List[str]] = None,
        notifier: Optional[AgentWebSocketNotifier] = None
    ) -> AgentResult:
        """Run PASTA analysis"""
        start_time = time.time()
        
        # Notify analysis start
        if notifier:
            await notifier.notify_analysis_start("PASTA")
        
        sections = await self.analyze_sections(context, section_ids, notifier)
        
        # Calculate token usage (estimate)
        total_tokens = len(context.system_description.split()) * 12  # PASTA is comprehensive
        
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
            await notifier.notify_analysis_complete("PASTA", success, error)
            
        return result
    
    def get_sections(self) -> List[Dict[str, str]]:
        """Return list of sections this agent can analyze"""
        return [
            {"id": "objectives", "title": "Business Objectives", "template": "table"},
            {"id": "technical_scope", "title": "Technical Scope", "template": "table"},
            {"id": "decomposition", "title": "Application Decomposition", "template": "diagram"},
            {"id": "threat_actors", "title": "Threat Actors", "template": "table"},
            {"id": "vulnerabilities", "title": "Vulnerabilities & Weaknesses", "template": "table"},
            {"id": "attack_scenarios", "title": "Attack Scenarios", "template": "table"},
            {"id": "risk_assessment", "title": "Risk Assessment", "template": "heat_map"},
            {"id": "remediation", "title": "Remediation Roadmap", "template": "table"}
        ]
    
    async def _parse_response(self, response: str, section_id: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        mapper = TemplateMapper()
        
        if section_id == "objectives":
            objectives = self._parse_objectives(response)
            return mapper.map_to_table(
                headers=["ID", "Objective", "Priority", "Impact Area", "Related Assets"],
                rows=[[
                    obj["id"],
                    obj["objective"],
                    obj["priority"],
                    obj["impact_area"],
                    ", ".join(obj.get("related_assets", []))
                ] for obj in objectives]
            )
            
        elif section_id == "technical_scope":
            scope = self._parse_technical_scope(response)
            return mapper.map_to_table(
                headers=["Component", "Technology", "Interfaces", "Dependencies"],
                rows=[[
                    item["component"],
                    item["technology"],
                    ", ".join(item.get("interfaces", [])),
                    ", ".join(item.get("dependencies", []))
                ] for item in scope]
            )
            
        elif section_id == "decomposition":
            decomp = self._parse_decomposition(response)
            return mapper.map_to_flow_diagram(
                nodes=decomp["nodes"],
                edges=decomp["edges"],
                layout="hierarchical"
            )
            
        elif section_id == "threat_actors":
            actors = self._parse_threat_actors(response)
            return mapper.map_to_table(
                headers=["Actor", "Type", "Motivation", "Capability", "Target Assets"],
                rows=[[
                    actor["name"],
                    actor["type"],
                    actor["motivation"],
                    actor["capability"],
                    ", ".join(actor.get("targets", []))
                ] for actor in actors]
            )
            
        elif section_id == "vulnerabilities":
            vulns = self._parse_vulnerabilities(response)
            return mapper.map_to_table(
                headers=["ID", "Component", "Vulnerability", "Severity", "Exploitability"],
                rows=[[
                    vuln["id"],
                    vuln["component"],
                    vuln["description"],
                    vuln["severity"],
                    vuln.get("exploitability", "Medium")
                ] for vuln in vulns]
            )
            
        elif section_id == "attack_scenarios":
            scenarios = self._parse_attack_scenarios(response)
            return mapper.map_to_table(
                headers=["Scenario", "Actor", "Attack Vector", "Impact", "Likelihood", "Risk"],
                rows=[[
                    scenario["name"],
                    scenario["actor"],
                    scenario["vector"],
                    scenario["impact"],
                    scenario["likelihood"],
                    scenario["risk"]
                ] for scenario in scenarios]
            )
            
        elif section_id == "risk_assessment":
            risks = self._parse_risks(response)
            return self._create_risk_heat_map(risks, mapper)
            
        elif section_id == "remediation":
            remediation = self._parse_remediation(response)
            return mapper.map_to_table(
                headers=["Priority", "Control", "Addresses", "Timeline", "Cost"],
                rows=[[
                    rem["priority"],
                    rem["control"],
                    rem["addresses"],
                    rem["timeline"],
                    rem.get("cost", "Medium")
                ] for rem in remediation]
            )
            
        else:
            return mapper.map_to_text(response, "markdown")
    
    def _parse_objectives(self, response: str) -> List[Dict[str, Any]]:
        """Parse business objectives from response"""
        objectives = []
        
        # Look for Stage 1 or objectives section
        obj_section = re.search(r"STAGE 1.*?OBJECTIVES?:(.*?)(?:STAGE 2|$)", response, re.IGNORECASE | re.DOTALL)
        if not obj_section:
            obj_section = re.search(r"Business Objectives?:(.*?)(?:Technical|Stage|$)", response, re.IGNORECASE | re.DOTALL)
            
        if obj_section:
            content = obj_section.group(1)
            
            # Parse individual objectives
            obj_pattern = r"(?:BO-\d+|Objective \d+):\s*(.+?)(?:Priority:|Impact:|$)"
            for match in re.finditer(obj_pattern, content, re.MULTILINE):
                objective_text = match.group(1).strip()
                
                # Extract priority
                priority_match = re.search(r"Priority:\s*(critical|high|medium|low)", content[match.start():], re.IGNORECASE)
                priority = priority_match.group(1).lower() if priority_match else "medium"
                
                # Extract impact area
                impact_match = re.search(r"Impact.*?:\s*(.+?)(?:\n|$)", content[match.start():], re.IGNORECASE)
                impact_area = impact_match.group(1).strip() if impact_match else "Operations"
                
                objectives.append({
                    "id": f"BO-{len(objectives)+1:03d}",
                    "objective": objective_text,
                    "priority": priority,
                    "impact_area": impact_area,
                    "related_assets": []
                })
                
        return objectives
    
    def _parse_technical_scope(self, response: str) -> List[Dict[str, Any]]:
        """Parse technical scope from response"""
        scope_items = []
        
        # Look for Stage 2 or technical scope section
        scope_section = re.search(r"STAGE 2.*?TECHNICAL SCOPE:(.*?)(?:STAGE 3|$)", response, re.IGNORECASE | re.DOTALL)
        if not scope_section:
            scope_section = re.search(r"Technical Scope:(.*?)(?:Application|Stage|$)", response, re.IGNORECASE | re.DOTALL)
            
        if scope_section:
            content = scope_section.group(1)
            
            # Parse components
            comp_pattern = r"(?:Component:|Technology:)\s*(.+?)(?:\n|$)"
            for match in re.finditer(comp_pattern, content, re.MULTILINE):
                component = match.group(1).strip()
                
                # Look for associated details
                details_text = content[match.start():match.start()+500]
                
                # Extract technology
                tech_match = re.search(r"(?:Technology|Stack):\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                technology = tech_match.group(1).strip() if tech_match else component
                
                scope_items.append({
                    "component": component,
                    "technology": technology,
                    "interfaces": [],
                    "dependencies": []
                })
                
        return scope_items
    
    def _parse_decomposition(self, response: str) -> Dict[str, Any]:
        """Parse application decomposition into diagram data"""
        nodes = []
        edges = []
        
        # Look for Stage 3 or decomposition section
        decomp_section = re.search(r"STAGE 3.*?DECOMPOSITION:(.*?)(?:STAGE 4|$)", response, re.IGNORECASE | re.DOTALL)
        
        if decomp_section:
            content = decomp_section.group(1)
            
            # Extract components as nodes
            comp_pattern = r"(?:Component|Process|Service):\s*(.+?)(?:\n|$)"
            for i, match in enumerate(re.finditer(comp_pattern, content, re.MULTILINE)):
                component = match.group(1).strip()
                nodes.append({
                    "id": f"node_{i}",
                    "label": component,
                    "type": "component"
                })
                
            # Extract data flows as edges
            flow_pattern = r"(.+?)\s*(?:->|flows to)\s*(.+?)(?:\n|$)"
            for match in re.finditer(flow_pattern, content, re.MULTILINE):
                source = match.group(1).strip()
                target = match.group(2).strip()
                
                # Find node IDs
                source_node = next((n for n in nodes if n["label"] == source), None)
                target_node = next((n for n in nodes if n["label"] == target), None)
                
                if source_node and target_node:
                    edges.append({
                        "id": f"edge_{len(edges)}",
                        "source": source_node["id"],
                        "target": target_node["id"],
                        "label": "data flow"
                    })
                    
        return {"nodes": nodes, "edges": edges}
    
    def _parse_threat_actors(self, response: str) -> List[Dict[str, Any]]:
        """Parse threat actors from response"""
        actors = []
        
        # Look for Stage 4 or threat analysis section
        threat_section = re.search(r"STAGE 4.*?THREAT.*?:(.*?)(?:STAGE 5|$)", response, re.IGNORECASE | re.DOTALL)
        
        if threat_section:
            content = threat_section.group(1)
            
            # Parse actors
            actor_pattern = r"(?:Actor|Threat).*?:\s*(.+?)(?:Motivation:|Capability:|$)"
            for match in re.finditer(actor_pattern, content, re.MULTILINE):
                actor_name = match.group(1).strip()
                
                # Extract details
                details_text = content[match.start():match.start()+500]
                
                # Motivation
                mot_match = re.search(r"Motivation:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                motivation = mot_match.group(1).strip() if mot_match else "Unknown"
                
                # Capability
                cap_match = re.search(r"Capability:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                capability = cap_match.group(1).strip() if cap_match else "Medium"
                
                # Determine actor type
                actor_type = self._classify_actor_type(actor_name, capability)
                
                actors.append({
                    "name": actor_name,
                    "type": actor_type,
                    "motivation": motivation,
                    "capability": capability,
                    "targets": []
                })
                
        return actors
    
    def _parse_vulnerabilities(self, response: str) -> List[Dict[str, Any]]:
        """Parse vulnerabilities from response"""
        vulns = []
        
        # Look for Stage 5 or vulnerability section
        vuln_section = re.search(r"STAGE 5.*?VULNERABILIT.*?:(.*?)(?:STAGE 6|$)", response, re.IGNORECASE | re.DOTALL)
        
        if vuln_section:
            content = vuln_section.group(1)
            
            # Parse vulnerabilities
            vuln_pattern = r"(?:CVE-\d+-\d+|Vulnerability|Weakness):\s*(.+?)(?:Component:|Severity:|$)"
            for match in re.finditer(vuln_pattern, content, re.MULTILINE):
                vuln_desc = match.group(1).strip()
                
                # Extract severity
                sev_match = re.search(r"Severity:\s*(critical|high|medium|low)", content[match.start():], re.IGNORECASE)
                severity = sev_match.group(1).lower() if sev_match else "medium"
                
                vulns.append({
                    "id": f"V-{len(vulns)+1:03d}",
                    "component": "System",  # Would need more parsing for specific component
                    "description": vuln_desc,
                    "severity": severity,
                    "exploitability": self._assess_exploitability(vuln_desc)
                })
                
        return vulns
    
    def _parse_attack_scenarios(self, response: str) -> List[Dict[str, Any]]:
        """Parse attack scenarios from response"""
        scenarios = []
        
        # Look for Stage 6 or attack modeling section
        attack_section = re.search(r"STAGE 6.*?ATTACK.*?:(.*?)(?:STAGE 7|$)", response, re.IGNORECASE | re.DOTALL)
        
        if attack_section:
            content = attack_section.group(1)
            
            # Parse scenarios
            scenario_pattern = r"(?:Scenario|Attack).*?:\s*(.+?)(?:Actor:|Vector:|$)"
            for match in re.finditer(scenario_pattern, content, re.MULTILINE):
                scenario_name = match.group(1).strip()
                
                # Extract details
                details_text = content[match.start():match.start()+500]
                
                # Actor
                actor_match = re.search(r"Actor:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                actor = actor_match.group(1).strip() if actor_match else "Unknown"
                
                # Attack vector
                vector_match = re.search(r"Vector:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                vector = vector_match.group(1).strip() if vector_match else "Unknown"
                
                # Assess likelihood and risk
                likelihood = self._assess_scenario_likelihood(details_text)
                risk = self._assess_scenario_risk(details_text)
                
                scenarios.append({
                    "name": scenario_name,
                    "actor": actor,
                    "vector": vector,
                    "impact": "High",  # Would need more parsing
                    "likelihood": likelihood,
                    "risk": risk
                })
                
        return scenarios
    
    def _parse_risks(self, response: str) -> List[Dict[str, Any]]:
        """Parse risk assessments from response"""
        risks = []
        
        # Look for Stage 7 or risk analysis section
        risk_section = re.search(r"STAGE 7.*?RISK.*?:(.*?)(?:REMEDIATION|$)", response, re.IGNORECASE | re.DOTALL)
        
        if risk_section:
            content = risk_section.group(1)
            
            # Parse risk entries
            risk_pattern = r"(?:R\d+|Risk).*?:\s*(.+?)(?:Impact:|Likelihood:|$)"
            for match in re.finditer(risk_pattern, content, re.MULTILINE):
                risk_desc = match.group(1).strip()
                
                # Extract metrics
                details_text = content[match.start():match.start()+300]
                
                # Business impact (1-5)
                bus_match = re.search(r"Business Impact:\s*(\d)", details_text, re.IGNORECASE)
                business_impact = int(bus_match.group(1)) if bus_match else 3
                
                # Likelihood (1-5)
                like_match = re.search(r"Likelihood:\s*(\d)", details_text, re.IGNORECASE)
                likelihood = int(like_match.group(1)) if like_match else 3
                
                risks.append({
                    "description": risk_desc,
                    "business_impact": business_impact,
                    "likelihood": likelihood,
                    "overall_risk": business_impact * likelihood
                })
                
        return risks
    
    def _parse_remediation(self, response: str) -> List[Dict[str, Any]]:
        """Parse remediation roadmap from response"""
        remediation = []
        
        # Look for remediation section
        rem_section = re.search(r"REMEDIATION.*?ROADMAP:(.*?)$", response, re.IGNORECASE | re.DOTALL)
        
        if rem_section:
            content = rem_section.group(1)
            
            # Parse priority levels
            for priority in ["Priority 1", "Immediate", "Critical", "Priority 2", "30 days", "Priority 3"]:
                priority_section = re.search(rf"{priority}.*?:(.*?)(?:Priority|$)", content, re.IGNORECASE | re.DOTALL)
                if priority_section:
                    controls_text = priority_section.group(1)
                    
                    # Parse controls
                    control_pattern = r"(?:Control:|-)?\s*(.+?)(?:Addresses|Timeline:|$)"
                    for match in re.finditer(control_pattern, controls_text, re.MULTILINE):
                        control = match.group(1).strip()
                        if control and len(control) > 5:  # Filter out noise
                            
                            # Extract what it addresses
                            addr_match = re.search(r"Addresses.*?:\s*(.+?)(?:\n|$)", controls_text[match.start():], re.IGNORECASE)
                            addresses = addr_match.group(1).strip() if addr_match else "Multiple risks"
                            
                            # Determine timeline based on priority
                            if "1" in priority or "Immediate" in priority:
                                timeline = "Immediate"
                            elif "2" in priority or "30" in priority:
                                timeline = "30 days"
                            else:
                                timeline = "90 days"
                                
                            remediation.append({
                                "priority": priority.split()[0] if priority.startswith("Priority") else "High",
                                "control": control,
                                "addresses": addresses,
                                "timeline": timeline,
                                "cost": "Medium"
                            })
                            
        return remediation
    
    def _create_risk_heat_map(self, risks: List[Dict[str, Any]], mapper: TemplateMapper) -> Dict[str, Any]:
        """Create risk heat map"""
        # Initialize 5x5 matrix
        matrix = [[0 for _ in range(5)] for _ in range(5)]
        
        # Populate matrix (likelihood on Y axis, impact on X axis)
        for risk in risks:
            likelihood = min(max(risk.get("likelihood", 3) - 1, 0), 4)  # 0-4 index
            impact = min(max(risk.get("business_impact", 3) - 1, 0), 4)  # 0-4 index
            matrix[4-likelihood][impact] += 1  # Invert Y for display
            
        return mapper.map_to_heat_map(
            x_labels=["Very Low", "Low", "Medium", "High", "Very High"],
            y_labels=["Very High", "High", "Medium", "Low", "Very Low"],
            data=matrix,
            title="Risk Assessment Matrix (Likelihood vs Impact)"
        )
    
    def _classify_actor_type(self, name: str, capability: str) -> str:
        """Classify threat actor type"""
        name_lower = name.lower()
        cap_lower = capability.lower()
        
        if any(word in name_lower for word in ['nation', 'state', 'apt']):
            return "nation-state"
        elif any(word in name_lower for word in ['criminal', 'organized', 'syndicate']):
            return "organized-crime"
        elif any(word in name_lower for word in ['hacktivist', 'activist']):
            return "hacktivist"
        elif any(word in name_lower for word in ['insider', 'employee']):
            return "insider"
        else:
            return "opportunist"
            
    def _assess_exploitability(self, vuln_desc: str) -> str:
        """Assess exploitability of vulnerability"""
        desc_lower = vuln_desc.lower()
        
        if any(word in desc_lower for word in ['easy', 'trivial', 'public exploit']):
            return "High"
        elif any(word in desc_lower for word in ['difficult', 'complex', 'requires']):
            return "Low"
        else:
            return "Medium"
            
    def _assess_scenario_likelihood(self, text: str) -> str:
        """Assess attack scenario likelihood"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['very likely', 'common', 'frequent']):
            return "very-high"
        elif any(word in text_lower for word in ['likely', 'probable']):
            return "high"
        elif any(word in text_lower for word in ['unlikely', 'rare']):
            return "low"
        elif any(word in text_lower for word in ['very unlikely', 'extremely rare']):
            return "very-low"
        else:
            return "medium"
            
    def _assess_scenario_risk(self, text: str) -> str:
        """Assess overall scenario risk"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['critical', 'severe', 'catastrophic']):
            return "critical"
        elif any(word in text_lower for word in ['high', 'significant']):
            return "high"
        elif any(word in text_lower for word in ['low', 'minimal']):
            return "low"
        else:
            return "medium"
    
    def _extract_artifacts(self, sections: List[SectionResult]) -> List[Dict[str, Any]]:
        """Extract key artifacts for other agents to use"""
        artifacts = []
        
        for section in sections:
            if section.section_id == "threat_actors" and section.status.value == "completed":
                artifacts.append({
                    "type": "threat_actors",
                    "name": "PASTA Threat Actors",
                    "data": section.content
                })
            elif section.section_id == "attack_scenarios" and section.status.value == "completed":
                artifacts.append({
                    "type": "attack_scenarios", 
                    "name": "PASTA Attack Scenarios",
                    "data": section.content
                })
            elif section.section_id == "risk_assessment" and section.status.value == "completed":
                artifacts.append({
                    "type": "risk_matrix",
                    "name": "PASTA Risk Assessment",
                    "data": section.content
                })
                
        return artifacts