"""
HAZOP Agent Implementation
Hazard and Operability Study for systematic hazard identification
"""
from typing import List, Dict, Any, Optional
import re
import time
from uuid import uuid4

from core.agents.base import BaseAnalysisAgent, SectionResult
from core.models.schemas import FrameworkType, AgentContext, AgentResult
from core.templates.mapper import TemplateMapper
from core.agents.websocket_integration import AgentWebSocketNotifier


class HazopAgent(BaseAnalysisAgent):
    """
    HAZOP Security Analysis Agent
    
    Analyzes system using guide words to identify:
    - Process deviations and their causes
    - Security and safety consequences
    - Operational hazards
    - Control failures
    - Recovery procedures
    """
    
    def __init__(self):
        super().__init__(FrameworkType.HAZOP)
        
    async def analyze(
        self, 
        context: AgentContext, 
        section_ids: Optional[List[str]] = None,
        notifier: Optional[AgentWebSocketNotifier] = None
    ) -> AgentResult:
        """Run HAZOP analysis"""
        start_time = time.time()
        
        # Notify analysis start
        if notifier:
            await notifier.notify_analysis_start("HAZOP")
        
        sections = await self.analyze_sections(context, section_ids, notifier)
        
        # Calculate token usage (estimate)
        total_tokens = len(context.system_description.split()) * 8  # HAZOP is systematic
        
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
            await notifier.notify_analysis_complete("HAZOP", success, error)
            
        return result
    
    def get_sections(self) -> List[Dict[str, str]]:
        """Return list of sections this agent can analyze"""
        return [
            {"id": "nodes", "title": "System Nodes", "template": "table"},
            {"id": "parameters", "title": "Critical Parameters", "template": "table"},
            {"id": "deviations", "title": "Deviation Analysis", "template": "table"},
            {"id": "risk_matrix", "title": "Risk Assessment Matrix", "template": "heat_map"},
            {"id": "safeguards", "title": "Safeguards", "template": "table"},
            {"id": "actions", "title": "Action Items", "template": "table"},
            {"id": "process_flow", "title": "Process Flow Diagram", "template": "diagram"},
            {"id": "recommendations", "title": "Safety Recommendations", "template": "section"}
        ]
    
    async def _parse_response(self, response: str, section_id: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        mapper = TemplateMapper()
        
        if section_id == "nodes":
            nodes = self._parse_nodes(response)
            return mapper.map_to_table(
                headers=["ID", "Node", "Function", "Inputs", "Outputs", "Criticality"],
                rows=[[
                    node["id"],
                    node["name"],
                    node["function"],
                    ", ".join(node.get("inputs", [])),
                    ", ".join(node.get("outputs", [])),
                    node.get("criticality", "Medium")
                ] for node in nodes]
            )
            
        elif section_id == "parameters":
            parameters = self._parse_parameters(response)
            return mapper.map_to_table(
                headers=["ID", "Parameter", "Node", "Normal Range", "Critical Limits", "Monitoring"],
                rows=[[
                    param["id"],
                    param["name"],
                    param["node"],
                    param.get("normal_range", "N/A"),
                    param.get("critical_limits", "N/A"),
                    param.get("monitoring", "Continuous")
                ] for param in parameters]
            )
            
        elif section_id == "deviations":
            deviations = self._parse_deviations(response)
            return mapper.map_to_table(
                headers=["ID", "Node", "Guide Word", "Parameter", "Deviation", "Causes", "Consequences", "Severity"],
                rows=[[
                    dev["id"],
                    dev["node"],
                    dev["guide_word"],
                    dev["parameter"],
                    dev["deviation"],
                    "; ".join(dev.get("causes", [])),
                    "; ".join(dev.get("consequences", [])),
                    dev.get("severity", "Medium")
                ] for dev in deviations]
            )
            
        elif section_id == "risk_matrix":
            deviations = self._parse_deviations(response)
            return self._create_risk_matrix(deviations, mapper)
            
        elif section_id == "safeguards":
            safeguards = self._parse_safeguards(response)
            return mapper.map_to_table(
                headers=["ID", "Safeguard", "Type", "Protects Against", "Effectiveness", "SIL"],
                rows=[[
                    guard["id"],
                    guard["name"],
                    guard["type"],
                    ", ".join(guard.get("protects_against", [])),
                    guard.get("effectiveness", "Medium"),
                    guard.get("sil", "N/A")
                ] for guard in safeguards]
            )
            
        elif section_id == "actions":
            actions = self._parse_actions(response)
            return mapper.map_to_table(
                headers=["ID", "Action", "Priority", "Type", "Owner", "Due Date", "Status"],
                rows=[[
                    action["id"],
                    action["description"],
                    action["priority"],
                    action["type"],
                    action.get("owner", "TBD"),
                    action.get("due_date", "TBD"),
                    action.get("status", "Open")
                ] for action in actions]
            )
            
        elif section_id == "process_flow":
            return self._parse_process_flow(response)
            
        elif section_id == "recommendations":
            return self._parse_recommendations(response)
            
        else:
            return mapper.map_to_text(response, "markdown")
    
    def _parse_nodes(self, response: str) -> List[Dict[str, Any]]:
        """Parse system nodes from response"""
        nodes = []
        
        # Look for nodes section
        nodes_section = re.search(r"NODES:(.*?)(?:PARAMETERS:|$)", response, re.IGNORECASE | re.DOTALL)
        
        if nodes_section:
            content = nodes_section.group(1)
            
            # Parse individual nodes
            node_pattern = r"NODE\s*\d*:\s*(.+?)(?:Function:|$)"
            for match in re.finditer(node_pattern, content, re.MULTILINE):
                node_name = match.group(1).strip()
                
                # Extract details
                details_text = content[match.start():match.start()+1000]
                
                # Function
                func_match = re.search(r"Function:\s*(.+?)(?:Inputs:|Outputs:|$)", details_text, re.IGNORECASE | re.DOTALL)
                function = func_match.group(1).strip() if func_match else "Processing"
                
                # Inputs
                inputs_match = re.search(r"Inputs:\s*(.+?)(?:Outputs:|Criticality:|$)", details_text, re.IGNORECASE | re.DOTALL)
                inputs = []
                if inputs_match:
                    inputs_text = inputs_match.group(1)
                    inputs = [i.strip() for i in re.findall(r"[-"]\s*(.+?)(?:\n|$)", inputs_text)]
                
                # Outputs
                outputs_match = re.search(r"Outputs:\s*(.+?)(?:Criticality:|NODE|$)", details_text, re.IGNORECASE | re.DOTALL)
                outputs = []
                if outputs_match:
                    outputs_text = outputs_match.group(1)
                    outputs = [o.strip() for o in re.findall(r"[-"]\s*(.+?)(?:\n|$)", outputs_text)]
                
                # Criticality
                crit_match = re.search(r"Criticality:\s*(\w+)", details_text, re.IGNORECASE)
                criticality = crit_match.group(1) if crit_match else self._assess_criticality(node_name)
                
                nodes.append({
                    "id": f"N-{len(nodes)+1:03d}",
                    "name": node_name,
                    "function": function,
                    "inputs": inputs,
                    "outputs": outputs,
                    "criticality": criticality
                })
                
        return nodes
    
    def _parse_parameters(self, response: str) -> List[Dict[str, Any]]:
        """Parse critical parameters from response"""
        parameters = []
        
        # Look for parameters section
        params_section = re.search(r"PARAMETERS:(.*?)(?:DEVIATIONS:|$)", response, re.IGNORECASE | re.DOTALL)
        
        if params_section:
            content = params_section.group(1)
            
            # Parse parameters
            param_pattern = r"P\d+:\s*(.+?)(?:Node:|Normal:|P\d+:|$)"
            for match in re.finditer(param_pattern, content, re.MULTILINE | re.DOTALL):
                param_desc = match.group(1).strip()
                
                # Extract details
                details_text = content[match.start():match.start()+500]
                
                # Node association
                node_match = re.search(r"Node:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                node = node_match.group(1).strip() if node_match else "System"
                
                # Normal range
                normal_match = re.search(r"Normal.*?:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                normal_range = normal_match.group(1).strip() if normal_match else "Defined"
                
                # Critical limits
                critical_match = re.search(r"Critical.*?:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                critical_limits = critical_match.group(1).strip() if critical_match else "See specifications"
                
                # Monitoring
                monitor_match = re.search(r"Monitor.*?:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                monitoring = monitor_match.group(1).strip() if monitor_match else "Continuous"
                
                parameters.append({
                    "id": f"P-{len(parameters)+1:03d}",
                    "name": param_desc.split(",")[0].strip(),
                    "node": node,
                    "normal_range": normal_range,
                    "critical_limits": critical_limits,
                    "monitoring": monitoring
                })
                
        return parameters
    
    def _parse_deviations(self, response: str) -> List[Dict[str, Any]]:
        """Parse HAZOP deviations from response"""
        deviations = []
        
        # HAZOP guide words
        guide_words = ["NO/NOT", "MORE", "LESS", "AS WELL AS", "PART OF", "REVERSE", "OTHER THAN", "EARLY", "LATE", "BEFORE", "AFTER"]
        
        # Look for deviations section
        dev_section = re.search(r"DEVIATIONS:(.*?)(?:SAFEGUARDS:|$)", response, re.IGNORECASE | re.DOTALL)
        
        if dev_section:
            content = dev_section.group(1)
            
            # Parse by guide word
            for guide_word in guide_words:
                # Find guide word section
                gw_pattern = rf"{guide_word}.*?:(.*?)(?:{'|'.join(guide_words)}|SAFEGUARDS|$)"
                gw_match = re.search(gw_pattern, content, re.IGNORECASE | re.DOTALL)
                
                if gw_match:
                    gw_content = gw_match.group(1)
                    
                    # Parse individual deviations
                    dev_pattern = r"(?:Deviation|Scenario):\s*(.+?)(?:Causes:|$)"
                    for dev_match in re.finditer(dev_pattern, gw_content, re.MULTILINE | re.DOTALL):
                        deviation_desc = dev_match.group(1).strip()
                        
                        # Extract details
                        details_text = gw_content[dev_match.start():dev_match.start()+1000]
                        
                        # Causes
                        causes_match = re.search(r"Causes:\s*(.+?)(?:Consequences:|$)", details_text, re.IGNORECASE | re.DOTALL)
                        causes = []
                        if causes_match:
                            causes_text = causes_match.group(1)
                            causes = [c.strip() for c in re.findall(r"[-"]\s*(.+?)(?:\n|$)", causes_text)]
                        
                        # Consequences
                        cons_match = re.search(r"Consequences:\s*(.+?)(?:Severity:|Deviation:|$)", details_text, re.IGNORECASE | re.DOTALL)
                        consequences = []
                        if cons_match:
                            cons_text = cons_match.group(1)
                            consequences = [c.strip() for c in re.findall(r"[-"]\s*(.+?)(?:\n|$)", cons_text)]
                        
                        # Severity
                        sev_match = re.search(r"Severity:\s*(\w+)", details_text, re.IGNORECASE)
                        severity = sev_match.group(1) if sev_match else self._assess_severity(consequences)
                        
                        # Extract node and parameter
                        node = self._extract_node_from_deviation(deviation_desc)
                        parameter = self._extract_parameter_from_deviation(deviation_desc)
                        
                        deviations.append({
                            "id": f"D-{len(deviations)+1:03d}",
                            "node": node,
                            "guide_word": guide_word,
                            "parameter": parameter,
                            "deviation": deviation_desc,
                            "causes": causes,
                            "consequences": consequences,
                            "severity": severity
                        })
                        
        return deviations
    
    def _parse_safeguards(self, response: str) -> List[Dict[str, Any]]:
        """Parse safeguards from response"""
        safeguards = []
        
        # Look for safeguards section
        safe_section = re.search(r"SAFEGUARDS:(.*?)(?:ACTIONS:|$)", response, re.IGNORECASE | re.DOTALL)
        
        if safe_section:
            content = safe_section.group(1)
            
            # Parse safeguards
            safe_pattern = r"SG\d+:\s*(.+?)(?:Type:|Protects:|SG\d+:|$)"
            for match in re.finditer(safe_pattern, content, re.MULTILINE | re.DOTALL):
                safeguard_desc = match.group(1).strip()
                
                # Extract details
                details_text = content[match.start():match.start()+500]
                
                # Type
                type_match = re.search(r"Type:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                guard_type = type_match.group(1).strip() if type_match else self._classify_safeguard_type(safeguard_desc)
                
                # Protects against
                prot_match = re.search(r"Protects.*?:\s*(.+?)(?:Effectiveness:|SIL:|$)", details_text, re.IGNORECASE | re.DOTALL)
                protects = []
                if prot_match:
                    prot_text = prot_match.group(1)
                    protects = [p.strip() for p in re.findall(r"[-"]\s*(.+?)(?:\n|$)", prot_text)]
                
                # Effectiveness
                eff_match = re.search(r"Effectiveness:\s*(\w+)", details_text, re.IGNORECASE)
                effectiveness = eff_match.group(1) if eff_match else "Medium"
                
                # SIL (Safety Integrity Level)
                sil_match = re.search(r"SIL:\s*(\d+)", details_text, re.IGNORECASE)
                sil = f"SIL{sil_match.group(1)}" if sil_match else "N/A"
                
                safeguards.append({
                    "id": f"SG-{len(safeguards)+1:03d}",
                    "name": safeguard_desc.split(",")[0].strip(),
                    "type": guard_type,
                    "protects_against": protects,
                    "effectiveness": effectiveness,
                    "sil": sil
                })
                
        return safeguards
    
    def _parse_actions(self, response: str) -> List[Dict[str, Any]]:
        """Parse action items from response"""
        actions = []
        
        # Look for actions section
        actions_section = re.search(r"ACTIONS:(.*?)$", response, re.IGNORECASE | re.DOTALL)
        
        if actions_section:
            content = actions_section.group(1)
            
            # Parse action items
            action_pattern = r"A\d+:\s*(.+?)(?:Priority:|Type:|A\d+:|$)"
            for match in re.finditer(action_pattern, content, re.MULTILINE | re.DOTALL):
                action_desc = match.group(1).strip()
                
                # Extract details
                details_text = content[match.start():match.start()+500]
                
                # Priority
                pri_match = re.search(r"Priority:\s*(\w+)", details_text, re.IGNORECASE)
                priority = pri_match.group(1) if pri_match else self._assess_action_priority(action_desc)
                
                # Type
                type_match = re.search(r"Type:\s*(.+?)(?:\n|$)", details_text, re.IGNORECASE)
                action_type = type_match.group(1).strip() if type_match else "Improvement"
                
                actions.append({
                    "id": f"A-{len(actions)+1:03d}",
                    "description": action_desc,
                    "priority": priority,
                    "type": action_type,
                    "owner": "TBD",
                    "due_date": "TBD",
                    "status": "Open"
                })
                
        return actions
    
    def _parse_process_flow(self, response: str) -> Dict[str, Any]:
        """Parse process flow diagram"""
        nodes = self._parse_nodes(response)
        
        # Create process flow diagram
        diagram_nodes = []
        edges = []
        
        for i, node in enumerate(nodes):
            diagram_nodes.append({
                "id": f"node_{i}",
                "label": node["name"],
                "type": "process",
                "data": {
                    "criticality": node.get("criticality", "Medium"),
                    "function": node.get("function", "")
                }
            })
        
        # Create edges based on inputs/outputs
        for i, node in enumerate(nodes):
            for output in node.get("outputs", []):
                # Find nodes that have this as input
                for j, target_node in enumerate(nodes):
                    if i != j and output in target_node.get("inputs", []):
                        edges.append({
                            "id": f"edge_{len(edges)}",
                            "source": f"node_{i}",
                            "target": f"node_{j}",
                            "label": output,
                            "type": "data_flow"
                        })
        
        mapper = TemplateMapper()
        return mapper.map_to_flow_diagram(
            nodes=diagram_nodes,
            edges=edges,
            layout="hierarchical"
        )
    
    def _parse_recommendations(self, response: str) -> Dict[str, Any]:
        """Parse safety recommendations"""
        content = "## HAZOP Safety Recommendations\n\n"
        
        # Look for recommendations in response
        rec_section = re.search(r"(?:RECOMMENDATIONS?|SUMMARY):(.*?)$", response, re.IGNORECASE | re.DOTALL)
        
        if rec_section:
            rec_content = rec_section.group(1)
            
            # Extract critical recommendations
            crit_match = re.search(r"Critical.*?:(.*?)(?:High Priority:|Medium Priority:|$)", rec_content, re.IGNORECASE | re.DOTALL)
            if crit_match:
                content += "### Critical Safety Actions\n"
                crit_items = re.findall(r"[-"]\s*(.+?)(?:\n|$)", crit_match.group(1), re.MULTILINE)
                for item in crit_items:
                    content += f"- {item.strip()}\n"
                content += "\n"
            
            # Extract high priority
            high_match = re.search(r"High Priority.*?:(.*?)(?:Medium Priority:|Low Priority:|$)", rec_content, re.IGNORECASE | re.DOTALL)
            if high_match:
                content += "### High Priority Improvements\n"
                high_items = re.findall(r"[-"]\s*(.+?)(?:\n|$)", high_match.group(1), re.MULTILINE)
                for item in high_items:
                    content += f"- {item.strip()}\n"
                content += "\n"
        
        # Add standard HAZOP recommendations
        content += """### HAZOP Best Practices
- Implement independent protection layers (IPL)
- Establish clear operational limits and alarms
- Regular deviation monitoring and trend analysis
- Automated safeguard testing procedures
- Comprehensive operator training on deviations
- Emergency response procedures for critical scenarios
- Periodic HAZOP review and updates
"""
        
        mapper = TemplateMapper()
        return mapper.map_to_text(content, "markdown")
    
    def _create_risk_matrix(self, deviations: List[Dict[str, Any]], mapper: TemplateMapper) -> Dict[str, Any]:
        """Create risk matrix from deviations"""
        # Initialize matrix
        matrix = {
            "low": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "medium": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "high": {"low": 0, "medium": 0, "high": 0, "critical": 0}
        }
        
        # Map severity to impact
        severity_to_impact = {
            "Low": "low",
            "Medium": "medium",
            "High": "high",
            "Critical": "critical"
        }
        
        # Assess likelihood based on causes
        for deviation in deviations:
            severity = deviation.get("severity", "Medium")
            impact = severity_to_impact.get(severity, "medium")
            
            # Assess likelihood based on number and type of causes
            num_causes = len(deviation.get("causes", []))
            if num_causes >= 3:
                likelihood = "high"
            elif num_causes >= 2:
                likelihood = "medium"
            else:
                likelihood = "low"
            
            if likelihood in matrix and impact in matrix[likelihood]:
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
            title="HAZOP Risk Matrix"
        )
    
    def _assess_criticality(self, name: str) -> str:
        """Assess node criticality"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ["auth", "security", "payment", "critical"]):
            return "Critical"
        elif any(word in name_lower for word in ["data", "process", "transaction"]):
            return "High"
        elif any(word in name_lower for word in ["backup", "log", "monitor"]):
            return "Low"
        else:
            return "Medium"
    
    def _assess_severity(self, consequences: List[str]) -> str:
        """Assess deviation severity based on consequences"""
        cons_text = " ".join(consequences).lower()
        
        if any(word in cons_text for word in ["catastrophic", "complete failure", "data loss", "breach"]):
            return "Critical"
        elif any(word in cons_text for word in ["significant", "major", "service disruption"]):
            return "High"
        elif any(word in cons_text for word in ["minor", "limited", "temporary"]):
            return "Low"
        else:
            return "Medium"
    
    def _extract_node_from_deviation(self, desc: str) -> str:
        """Extract node name from deviation description"""
        # Look for common patterns
        node_match = re.search(r"(?:at|in|from)\s+(?:the\s+)?(\w+(?:\s+\w+)?)\s*(?:node|system|component)", desc, re.IGNORECASE)
        if node_match:
            return node_match.group(1).strip()
        
        # Default to first significant words
        words = desc.split()[:2]
        return " ".join(words)
    
    def _extract_parameter_from_deviation(self, desc: str) -> str:
        """Extract parameter from deviation description"""
        # Look for common parameter patterns
        param_match = re.search(r"(?:flow|rate|pressure|temperature|speed|volume|level|time)\s*(?:of\s+)?(\w+)?", desc, re.IGNORECASE)
        if param_match:
            return param_match.group(0).strip()
        
        return "Process parameter"
    
    def _classify_safeguard_type(self, desc: str) -> str:
        """Classify safeguard type"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["alarm", "alert", "warning"]):
            return "Alarm"
        elif any(word in desc_lower for word in ["interlock", "shutdown", "trip"]):
            return "Interlock"
        elif any(word in desc_lower for word in ["relief", "vent", "overflow"]):
            return "Relief"
        elif any(word in desc_lower for word in ["procedure", "manual", "operator"]):
            return "Procedural"
        else:
            return "Control"
    
    def _assess_action_priority(self, desc: str) -> str:
        """Assess action priority"""
        desc_lower = desc.lower()
        
        if any(word in desc_lower for word in ["immediate", "critical", "urgent"]):
            return "Critical"
        elif any(word in desc_lower for word in ["important", "significant", "high"]):
            return "High"
        elif any(word in desc_lower for word in ["low", "minor", "optional"]):
            return "Low"
        else:
            return "Medium"
    
    def _extract_artifacts(self, sections: List[SectionResult]) -> List[Dict[str, Any]]:
        """Extract key artifacts for other agents to use"""
        artifacts = []
        
        for section in sections:
            if section.section_id == "deviations" and section.status.value == "completed":
                artifacts.append({
                    "type": "hazop_deviations",
                    "name": "HAZOP Deviation Analysis",
                    "data": section.content
                })
            elif section.section_id == "safeguards" and section.status.value == "completed":
                artifacts.append({
                    "type": "safety_controls",
                    "name": "HAZOP Safeguards",
                    "data": section.content
                })
            elif section.section_id == "risk_matrix" and section.status.value == "completed":
                artifacts.append({
                    "type": "risk_assessment",
                    "name": "HAZOP Risk Matrix",
                    "data": section.content
                })
                
        return artifacts
