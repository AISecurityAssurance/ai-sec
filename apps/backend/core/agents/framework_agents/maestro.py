"""
MAESTRO Agent Implementation
Multi-Agent Evaluated Securely Through Rigorous Oversight - for AI/ML security
"""
from typing import List, Dict, Any, Optional
import re
import time
from uuid import uuid4

from core.agents.base import BaseAnalysisAgent, SectionResult
from core.models.schemas import FrameworkType, AgentContext, AgentResult
from core.templates.mapper import TemplateMapper
from core.agents.websocket_integration import AgentWebSocketNotifier


class MaestroAgent(BaseAnalysisAgent):
    """
    MAESTRO Security Analysis Agent
    
    Analyzes AI/ML systems for:
    - Mission alignment and security objectives
    - Asset identification (agents, models, data)
    - Entry points and attack surfaces
    - Security controls
    - AI-specific threats
    - Risk assessment
    - Operational security
    """
    
    def __init__(self):
        super().__init__(FrameworkType.MAESTRO)
        
    async def analyze(
        self, 
        context: AgentContext, 
        section_ids: Optional[List[str]] = None,
        notifier: Optional[AgentWebSocketNotifier] = None
    ) -> AgentResult:
        """Run MAESTRO analysis"""
        start_time = time.time()
        
        # Notify analysis start
        if notifier:
            await notifier.notify_analysis_start("MAESTRO")
        
        sections = await self.analyze_sections(context, section_ids, notifier)
        
        # Calculate token usage (estimate)
        total_tokens = len(context.system_description.split()) * 10  # AI analysis is comprehensive
        
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
            await notifier.notify_analysis_complete("MAESTRO", success, error)
            
        return result
    
    def get_sections(self) -> List[Dict[str, str]]:
        """Return list of sections this agent can analyze"""
        return [
            {"id": "mission", "title": "Mission & Objectives", "template": "section"},
            {"id": "assets", "title": "AI/ML Assets", "template": "table"},
            {"id": "entrypoints", "title": "Entry Points", "template": "table"},
            {"id": "controls", "title": "Security Controls", "template": "table"},
            {"id": "threats", "title": "AI-Specific Threats", "template": "table"},
            {"id": "risk_matrix", "title": "Risk Assessment", "template": "heat_map"},
            {"id": "operations", "title": "Operational Security", "template": "section"},
            {"id": "agent_interactions", "title": "Agent Interactions", "template": "diagram"}
        ]
    
    async def _parse_response(self, response: str, section_id: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        mapper = TemplateMapper()
        
        if section_id == "mission":
            return self._parse_mission(response)
            
        elif section_id == "assets":
            assets = self._parse_assets(response)
            return mapper.map_to_table(
                headers=["ID", "Name", "Type", "Capabilities", "Trust Level", "Data Access"],
                rows=[[
                    asset["id"],
                    asset["name"],
                    asset["type"],
                    ", ".join(asset.get("capabilities", []))[:50] + "...",
                    asset.get("trust_level", "Unknown"),
                    ", ".join(asset.get("data_access", []))[:50] + "..."
                ] for asset in assets]
            )
            
        elif section_id == "entrypoints":
            entrypoints = self._parse_entrypoints(response)
            return mapper.map_to_table(
                headers=["ID", "Entry Point", "Type", "Authentication", "Risk Level"],
                rows=[[
                    ep["id"],
                    ep["name"],
                    ep["type"],
                    ep.get("authentication", "None"),
                    ep.get("risk_level", "Medium")
                ] for ep in entrypoints]
            )
            
        elif section_id == "controls":
            controls = self._parse_controls(response)
            return mapper.map_to_table(
                headers=["ID", "Control", "Type", "Coverage", "Effectiveness"],
                rows=[[
                    control["id"],
                    control["name"],
                    control["type"],
                    ", ".join(control.get("coverage", [])),
                    control.get("effectiveness", "Medium")
                ] for control in controls]
            )
            
        elif section_id == "threats":
            threats = self._parse_threats(response)
            return mapper.map_to_table(
                headers=["ID", "Threat", "Category", "Target", "Likelihood", "Impact", "Detection"],
                rows=[[
                    threat["id"],
                    threat["description"],
                    threat["category"],
                    threat.get("target", "System"),
                    threat["likelihood"],
                    threat["impact"],
                    threat.get("detection_difficulty", "Moderate")
                ] for threat in threats]
            )
            
        elif section_id == "risk_matrix":
            threats = self._parse_threats(response)
            return self._create_risk_matrix(threats, mapper)
            
        elif section_id == "operations":
            return self._parse_operations(response)
            
        elif section_id == "agent_interactions":
            return self._parse_agent_interactions(response)
            
        else:
            return mapper.map_to_text(response, "markdown")
    
    def _parse_mission(self, response: str) -> Dict[str, Any]:
        """Parse mission and objectives section"""
        # Extract mission statement
        mission_match = re.search(r"(?:Primary Purpose|Mission):\s*(.+?)(?:Security Objectives:|$)", 
                                response, re.IGNORECASE | re.DOTALL)
        mission = mission_match.group(1).strip() if mission_match else "Not specified"
        
        # Extract security objectives
        objectives = []
        obj_section = re.search(r"Security Objectives:(.*?)(?:A\s*-\s*ASSETS|$)", response, re.IGNORECASE | re.DOTALL)
        if obj_section:
            obj_text = obj_section.group(1)
            obj_items = re.findall(r"[-"]\s*(.+?)(?:\n|$)", obj_text, re.MULTILINE)
            objectives = [obj.strip() for obj in obj_items if obj.strip()]
        
        content = f"""## Mission Statement
{mission}

## Security Objectives
{chr(10).join(f'- {obj}' for obj in objectives)}

## AI/ML Security Focus
This system contains AI/ML components that require special security consideration:
- Model integrity and robustness
- Data privacy and protection
- Bias and fairness monitoring
- Explainability and transparency
- Adversarial resistance
"""
        
        mapper = TemplateMapper()
        return mapper.map_to_text(content, "markdown")
    
    def _parse_assets(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI/ML assets from response"""
        assets = []
        
        # Look for assets section
        assets_section = re.search(r"A\s*-\s*ASSETS:(.*?)(?:E\s*-\s*ENTRYPOINTS|$)", response, re.IGNORECASE | re.DOTALL)
        
        if assets_section:
            content = assets_section.group(1)
            
            # Parse agents
            agent_pattern = r"(?:Agent|Model|AI).*?:\s*(.+?)(?:Capabilities:|Trust Level:|$)"
            for match in re.finditer(agent_pattern, content, re.MULTILINE):
                agent_name = match.group(1).strip()
                
                # Extract details from following text
                details_text = content[match.start():match.start()+1000]
                
                # Capabilities
                cap_match = re.search(r"Capabilities:\s*(.+?)(?:Trust Level:|Data Access:|$)", details_text, re.IGNORECASE | re.DOTALL)
                capabilities = []
                if cap_match:
                    cap_text = cap_match.group(1)
                    capabilities = [c.strip() for c in re.findall(r"[-"]\s*(.+?)(?:\n|$)", cap_text)]
                
                # Trust level
                trust_match = re.search(r"Trust Level:\s*(\w+)", details_text, re.IGNORECASE)
                trust_level = trust_match.group(1) if trust_match else "partially-trusted"
                
                # Data access
                data_match = re.search(r"Data Access:\s*(.+?)(?:Agent:|Model:|$)", details_text, re.IGNORECASE | re.DOTALL)
                data_access = []
                if data_match:
                    data_text = data_match.group(1)
                    data_access = [d.strip() for d in re.findall(r"[-"]\s*(.+?)(?:\n|$)", data_text)]
                
                # Determine type
                agent_type = self._classify_agent_type(agent_name, capabilities)
                
                assets.append({
                    "id": f"MA-{len(assets)+1:03d}",
                    "name": agent_name,
                    "type": agent_type,
                    "capabilities": capabilities,
                    "trust_level": trust_level,
                    "data_access": data_access
                })
                
        return assets
    
    def _parse_entrypoints(self, response: str) -> List[Dict[str, Any]]:
        """Parse entry points from response"""
        entrypoints = []
        
        # Look for entrypoints section
        ep_section = re.search(r"E\s*-\s*ENTRYPOINTS:(.*?)(?:S\s*-\s*SECURITY|$)", response, re.IGNORECASE | re.DOTALL)
        
        if ep_section:
            content = ep_section.group(1)
            
            # Parse entry points
            ep_pattern = r"EP\d+:\s*(.+?)(?:Authentication:|Type:|EP\d+:|$)"
            for match in re.finditer(ep_pattern, content, re.MULTILINE | re.DOTALL):
                ep_desc = match.group(1).strip()
                
                # Extract authentication
                auth_match = re.search(r"Authentication.*?:\s*(.+?)(?:\n|$)", content[match.start():], re.IGNORECASE)
                authentication = auth_match.group(1).strip() if auth_match else "Required"
                
                # Classify type and risk
                ep_type = self._classify_entrypoint_type(ep_desc)
                risk_level = self._assess_entrypoint_risk(ep_desc, authentication)
                
                entrypoints.append({
                    "id": f"EP-{len(entrypoints)+1:03d}",
                    "name": ep_desc.split(",")[0].strip(),
                    "type": ep_type,
                    "authentication": authentication,
                    "risk_level": risk_level
                })
                
        return entrypoints
    
    def _parse_controls(self, response: str) -> List[Dict[str, Any]]:
        """Parse security controls from response"""
        controls = []
        
        # Look for security controls section
        controls_section = re.search(r"S\s*-\s*SECURITY CONTROLS:(.*?)(?:T\s*-\s*THREATS|$)", response, re.IGNORECASE | re.DOTALL)
        
        if controls_section:
            content = controls_section.group(1)
            
            # Parse controls
            control_pattern = r"SC\d+:\s*(.+?)(?:Coverage:|Type:|SC\d+:|$)"
            for match in re.finditer(control_pattern, content, re.MULTILINE | re.DOTALL):
                control_desc = match.group(1).strip()
                
                # Extract coverage
                cov_match = re.search(r"Coverage:\s*(.+?)(?:\n|$)", content[match.start():], re.IGNORECASE)
                coverage = [cov_match.group(1).strip()] if cov_match else ["General"]
                
                # Determine type and effectiveness
                control_type = self._classify_control_type(control_desc)
                effectiveness = self._assess_control_effectiveness(control_desc)
                
                controls.append({
                    "id": f"SC-{len(controls)+1:03d}",
                    "name": control_desc.split(",")[0].strip(),
                    "type": control_type,
                    "coverage": coverage,
                    "effectiveness": effectiveness
                })
                
        return controls
    
    def _parse_threats(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI-specific threats from response"""
        threats = []
        
        # Look for threats section
        threats_section = re.search(r"T\s*-\s*THREATS:(.*?)(?:R\s*-\s*RISKS|$)", response, re.IGNORECASE | re.DOTALL)
        
        if threats_section:
            content = threats_section.group(1)
            
            # Parse threats
            threat_pattern = r"TH\d+:\s*(.+?)(?:Type:|Attack Vector:|TH\d+:|$)"
            for match in re.finditer(threat_pattern, content, re.MULTILINE | re.DOTALL):
                threat_desc = match.group(1).strip()
                
                # Extract type/category
                type_match = re.search(r"Type:\s*(.+?)(?:\n|$)", content[match.start():], re.IGNORECASE)
                threat_type = type_match.group(1).strip() if type_match else self._classify_ai_threat(threat_desc)
                
                # Extract attack vector
                vector_match = re.search(r"Attack Vector:\s*(.+?)(?:\n|$)", content[match.start():], re.IGNORECASE)
                
                # Assess likelihood and impact
                likelihood = self._assess_ai_threat_likelihood(threat_desc)
                impact = self._assess_ai_threat_impact(threat_desc)
                detection = self._assess_detection_difficulty(threat_desc)
                
                threats.append({
                    "id": f"TH-{len(threats)+1:03d}",
                    "description": threat_desc,
                    "category": threat_type,
                    "likelihood": likelihood,
                    "impact": impact,
                    "detection_difficulty": detection
                })
                
        return threats
    
    def _parse_operations(self, response: str) -> Dict[str, Any]:
        """Parse operational security section"""
        # Look for operations section
        ops_section = re.search(r"O\s*-\s*OPERATIONS:(.*?)$", response, re.IGNORECASE | re.DOTALL)
        
        content = "## Operational Security Requirements\n\n"
        
        if ops_section:
            ops_content = ops_section.group(1)
            
            # Extract monitoring requirements
            mon_match = re.search(r"Monitoring:\s*(.+?)(?:Response:|$)", ops_content, re.IGNORECASE | re.DOTALL)
            if mon_match:
                content += "### Monitoring Requirements\n"
                content += mon_match.group(1).strip() + "\n\n"
            
            # Extract response procedures
            resp_match = re.search(r"Response:\s*(.+?)(?:Update:|$)", ops_content, re.IGNORECASE | re.DOTALL)
            if resp_match:
                content += "### Incident Response\n"
                content += resp_match.group(1).strip() + "\n\n"
        
        # Add AI-specific operational considerations
        content += """### AI/ML Specific Operations
- Model performance monitoring and drift detection
- Adversarial input detection and filtering
- Bias and fairness metrics tracking
- Model versioning and rollback procedures
- Data quality monitoring
- Explainability logging for critical decisions
"""
        
        mapper = TemplateMapper()
        return mapper.map_to_text(content, "markdown")
    
    def _parse_agent_interactions(self, response: str) -> Dict[str, Any]:
        """Parse agent interaction diagram"""
        assets = self._parse_assets(response)
        
        nodes = []
        edges = []
        
        # Create nodes for each agent/asset
        for i, asset in enumerate(assets):
            nodes.append({
                "id": f"node_{i}",
                "label": asset["name"],
                "type": asset["type"].lower().replace(" ", "_"),
                "data": {
                    "trust_level": asset.get("trust_level", "unknown"),
                    "capabilities": len(asset.get("capabilities", []))
                }
            })
        
        # Extract interactions (simplified - would need more sophisticated parsing)
        # Look for patterns like "Agent A communicates with Agent B"
        interaction_pattern = r"(.+?)\s*(?:communicates with|connects to|interacts with|sends data to)\s*(.+?)(?:\.|,|\n|$)"
        
        for match in re.finditer(interaction_pattern, response, re.IGNORECASE):
            source_name = match.group(1).strip()
            target_name = match.group(2).strip()
            
            # Find matching nodes
            source_node = next((n for n in nodes if source_name.lower() in n["label"].lower()), None)
            target_node = next((n for n in nodes if target_name.lower() in n["label"].lower()), None)
            
            if source_node and target_node:
                edges.append({
                    "id": f"edge_{len(edges)}",
                    "source": source_node["id"],
                    "target": target_node["id"],
                    "label": "interacts",
                    "type": "data_flow"
                })
        
        mapper = TemplateMapper()
        return mapper.map_to_flow_diagram(
            nodes=nodes,
            edges=edges,
            layout="force"
        )
    
    def _create_risk_matrix(self, threats: List[Dict[str, Any]], mapper: TemplateMapper) -> Dict[str, Any]:
        """Create risk matrix for AI threats"""
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
            title="AI Threat Risk Matrix"
        )
    
    def _classify_agent_type(self, name: str, capabilities: List[str]) -> str:
        """Classify AI agent type"""
        name_lower = name.lower()
        caps_str = " ".join(capabilities).lower()
        
        if "assistant" in name_lower or "chatbot" in name_lower:
            return "AI Assistant"
        elif "model" in name_lower or "ml" in name_lower:
            return "ML Model"
        elif "decision" in name_lower or "engine" in name_lower:
            return "Decision Engine"
        elif "automation" in name_lower or "rpa" in name_lower:
            return "Automation Agent"
        else:
            return "AI Component"
    
    def _classify_entrypoint_type(self, desc: str) -> str:
        """Classify entry point type"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["prompt", "input", "query"]):
            return "User Input"
        elif any(word in desc_lower for word in ["api", "endpoint", "service"]):
            return "API"
        elif any(word in desc_lower for word in ["file", "upload", "import"]):
            return "File Upload"
        elif any(word in desc_lower for word in ["agent", "communication", "message"]):
            return "Agent Communication"
        else:
            return "Interface"
    
    def _assess_entrypoint_risk(self, desc: str, auth: str) -> str:
        """Assess entry point risk level"""
        desc_lower = desc.lower()
        auth_lower = auth.lower()
        
        if "none" in auth_lower or "public" in auth_lower:
            return "High"
        elif any(word in desc_lower for word in ["admin", "privileged", "sensitive"]):
            return "High"
        elif "required" in auth_lower and "multi" in auth_lower:
            return "Low"
        else:
            return "Medium"
    
    def _classify_control_type(self, desc: str) -> str:
        """Classify security control type"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["prevent", "block", "filter", "validate"]):
            return "Preventive"
        elif any(word in desc_lower for word in ["detect", "monitor", "alert", "log"]):
            return "Detective"
        elif any(word in desc_lower for word in ["recover", "restore", "rollback"]):
            return "Corrective"
        else:
            return "Administrative"
    
    def _assess_control_effectiveness(self, desc: str) -> str:
        """Assess control effectiveness"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["comprehensive", "strong", "robust"]):
            return "High"
        elif any(word in desc_lower for word in ["basic", "limited", "partial"]):
            return "Low"
        else:
            return "Medium"
    
    def _classify_ai_threat(self, desc: str) -> str:
        """Classify AI-specific threat type"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["adversarial", "evasion", "perturbation"]):
            return "Adversarial"
        elif any(word in desc_lower for word in ["poisoning", "backdoor", "contamination"]):
            return "Data Poisoning"
        elif any(word in desc_lower for word in ["extraction", "inversion", "steal"]):
            return "Model Theft"
        elif any(word in desc_lower for word in ["privacy", "leakage", "memorization"]):
            return "Privacy Breach"
        elif any(word in desc_lower for word in ["bias", "discrimination", "fairness"]):
            return "Bias"
        elif any(word in desc_lower for word in ["hallucination", "confabulation", "false"]):
            return "Hallucination"
        elif any(word in desc_lower for word in ["prompt", "injection", "jailbreak"]):
            return "Prompt Injection"
        else:
            return "AI Misuse"
    
    def _assess_ai_threat_likelihood(self, desc: str) -> str:
        """Assess AI threat likelihood"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["easy", "common", "frequent", "trivial"]):
            return "high"
        elif any(word in desc_lower for word in ["difficult", "rare", "complex"]):
            return "low"
        else:
            return "medium"
    
    def _assess_ai_threat_impact(self, desc: str) -> str:
        """Assess AI threat impact"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["critical", "severe", "catastrophic", "complete"]):
            return "critical"
        elif any(word in desc_lower for word in ["significant", "major", "serious"]):
            return "high"
        elif any(word in desc_lower for word in ["minor", "limited", "minimal"]):
            return "low"
        else:
            return "medium"
    
    def _assess_detection_difficulty(self, desc: str) -> str:
        """Assess how difficult it is to detect the threat"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["subtle", "hidden", "sophisticated"]):
            return "Very Hard"
        elif any(word in desc_lower for word in ["complex", "advanced"]):
            return "Hard"
        elif any(word in desc_lower for word in ["obvious", "simple", "basic"]):
            return "Easy"
        else:
            return "Moderate"
    
    def _extract_artifacts(self, sections: List[SectionResult]) -> List[Dict[str, Any]]:
        """Extract key artifacts for other agents to use"""
        artifacts = []
        
        for section in sections:
            if section.section_id == "assets" and section.status.value == "completed":
                artifacts.append({
                    "type": "ai_assets",
                    "name": "MAESTRO AI/ML Assets",
                    "data": section.content
                })
            elif section.section_id == "threats" and section.status.value == "completed":
                artifacts.append({
                    "type": "ai_threats",
                    "name": "MAESTRO AI Threats",
                    "data": section.content
                })
            elif section.section_id == "agent_interactions" and section.status.value == "completed":
                artifacts.append({
                    "type": "agent_architecture",
                    "name": "MAESTRO Agent Architecture",
                    "data": section.content
                })
                
        return artifacts