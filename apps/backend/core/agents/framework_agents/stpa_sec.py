"""
STPA-Sec Agent Implementation
This is a critical agent as it defines the system structure used by other analyses.
"""
from typing import List, Dict, Any, Optional
import json
import re
import time
from uuid import uuid4
from sqlalchemy.orm import Session

from core.agents.base import BaseAnalysisAgent
from core.agents.types import SectionResult
from core.models.schemas import FrameworkType, AgentContext, AgentResult
from core.templates.mapper import TemplateMapper, create_threat_table
from core.agents.websocket_integration import AgentWebSocketNotifier
from storage.repositories.stpa_sec import STPASecRepository
from core.database import get_db


class StpaSecAgent(BaseAnalysisAgent):
    """
    STPA-Sec Analysis Agent
    
    Implements:
    1. Step 1: Define losses, hazards, and system constraints
    2. Step 2: Model control structure
    3. Step 3: Identify unsafe control actions
    4. Step 4: Identify causal scenarios
    """
    
    def __init__(self, db_session: Optional[Session] = None):
        super().__init__(FrameworkType.STPA_SEC)
        self.db_session = db_session
        self.repository = None
        
    async def analyze(
        self, 
        context: AgentContext, 
        section_ids: Optional[List[str]] = None,
        notifier: Optional['AgentWebSocketNotifier'] = None,
        save_to_db: bool = True
    ) -> AgentResult:
        """Run STPA-Sec analysis"""
        start_time = time.time()
        
        # Initialize database session if needed
        if save_to_db and not self.db_session:
            self.db_session = next(get_db())
            self.repository = STPASecRepository(self.db_session)
        elif save_to_db and self.db_session:
            self.repository = STPASecRepository(self.db_session)
        
        # Notify analysis start
        if notifier:
            await notifier.notify_analysis_start("STPA-Sec")
        
        sections = await self.analyze_sections(context, section_ids, notifier)
        
        # Calculate token usage (estimate)
        total_tokens = len(context.system_description.split()) * 10  # Rough estimate
        
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
            await notifier.notify_analysis_complete("STPA-Sec", success, error)
        
        # Save to database if enabled
        if save_to_db and self.repository and success:
            try:
                # Convert sections list to dict for easier access
                sections_dict = {s.id: s.model_dump() for s in sections}
                result.sections = sections_dict
                
                # Save analysis to database
                analysis_id = self.repository.save_analysis(context, result)
                
                # Add database ID to result metadata
                result.metadata = result.metadata or {}
                result.metadata['database_id'] = analysis_id
                result.metadata['saved_to_database'] = True
                
                print(f"STPA-Sec analysis saved to database with ID: {analysis_id}")
            except Exception as e:
                print(f"Failed to save STPA-Sec analysis to database: {str(e)}")
                result.metadata = result.metadata or {}
                result.metadata['database_error'] = str(e)
                result.metadata['saved_to_database'] = False
            
        return result
    
    def get_sections(self) -> List[Dict[str, str]]:
        """Return list of sections this agent can analyze"""
        return [
            {"id": "system_definition", "title": "System Definition", "template": "section"},
            {"id": "losses", "title": "Losses", "template": "table"},
            {"id": "hazards", "title": "Hazards", "template": "table"},
            {"id": "constraints", "title": "Security Constraints", "template": "table"},
            {"id": "control_structure", "title": "Control Structure", "template": "diagram"},
            {"id": "control_actions", "title": "Control Actions", "template": "table"},
            {"id": "feedback_loops", "title": "Feedback Loops", "template": "table"},
            {"id": "ucas", "title": "Unsafe Control Actions", "template": "table"},
            {"id": "causal_scenarios", "title": "Causal Scenarios", "template": "table"},
            {"id": "security_controls", "title": "Security Controls", "template": "table"}
        ]
    
    async def _parse_response(self, response: str, section_id: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        mapper = TemplateMapper()
        
        if section_id == "system_definition":
            return self._parse_system_definition(response)
        
        elif section_id == "losses":
            losses = self._parse_losses(response)
            return mapper.map_to_table(
                headers=["ID", "Description", "Type", "Stakeholders", "Severity"],
                rows=[[
                    loss["id"],
                    loss["description"],
                    loss["type"],
                    ", ".join(loss.get("stakeholders", [])),
                    loss.get("severity", "High")
                ] for loss in losses]
            )
        
        elif section_id == "hazards":
            hazards = self._parse_hazards(response)
            return mapper.map_to_table(
                headers=["ID", "Description", "System State", "Linked Losses"],
                rows=[[
                    hazard["id"],
                    hazard["description"],
                    hazard["system_state"],
                    ", ".join(hazard.get("linked_losses", []))
                ] for hazard in hazards]
            )
        
        elif section_id == "constraints":
            constraints = self._parse_constraints(response)
            return mapper.map_to_table(
                headers=["ID", "Constraint", "Type", "Related Hazards"],
                rows=[[
                    constraint["id"],
                    constraint["description"],
                    constraint.get("type", "Preventive"),
                    ", ".join(constraint.get("related_hazards", []))
                ] for constraint in constraints]
            )
        
        elif section_id == "control_structure":
            structure = self._parse_control_structure(response)
            return mapper.map_to_flow_diagram(
                nodes=structure["nodes"],
                edges=structure["edges"],
                layout="hierarchical"
            )
        
        elif section_id == "control_actions":
            actions = self._parse_control_actions(response)
            return mapper.map_to_table(
                headers=["ID", "Controller", "Action", "Controlled Process", "Type"],
                rows=[[
                    action["id"],
                    action["controller"],
                    action["action"],
                    action["controlled_process"],
                    action.get("type", "Command")
                ] for action in actions]
            )
        
        elif section_id == "feedback_loops":
            feedbacks = self._parse_feedback_loops(response)
            return mapper.map_to_table(
                headers=["ID", "Source", "Information", "Destination", "Purpose"],
                rows=[[
                    fb["id"],
                    fb["source"],
                    fb["information"],
                    fb["destination"],
                    fb.get("purpose", "")
                ] for fb in feedbacks]
            )
        
        elif section_id == "ucas":
            ucas = self._parse_ucas(response)
            return mapper.map_to_table(
                headers=["ID", "Control Action", "Type", "Context", "Hazards", "STRIDE"],
                rows=[[
                    uca["id"],
                    uca["control_action"],
                    uca["type"],
                    uca["context"],
                    ", ".join(uca.get("linked_hazards", [])),
                    ", ".join(uca.get("stride_categories", []))
                ] for uca in ucas]
            )
        
        elif section_id == "causal_scenarios":
            scenarios = self._parse_causal_scenarios(response)
            return mapper.map_to_table(
                headers=["ID", "UCA", "Scenario", "Causal Factors", "Attack Complexity"],
                rows=[[
                    scenario["id"],
                    scenario["uca_id"],
                    scenario["description"],
                    "; ".join(scenario.get("causal_factors", [])),
                    scenario.get("complexity", "Medium")
                ] for scenario in scenarios]
            )
        
        elif section_id == "security_controls":
            controls = self._parse_security_controls(response)
            return mapper.map_to_table(
                headers=["ID", "Control", "Type", "Priority", "Related Scenarios"],
                rows=[[
                    control["id"],
                    control["description"],
                    control["type"],
                    control["priority"],
                    ", ".join(control.get("related_scenarios", []))
                ] for control in controls]
            )
        
        else:
            # Default to text
            return mapper.map_to_text(response, "markdown")
    
    def _parse_system_definition(self, response: str) -> Dict[str, Any]:
        """Parse system definition from response"""
        # Extract system purpose statement
        purpose_match = re.search(r"System Purpose:?\s*(.+?)(?:\n|$)", response, re.IGNORECASE)
        purpose = purpose_match.group(1).strip() if purpose_match else "System purpose not specified"
        
        # Extract boundaries
        in_scope = re.findall(r"In Scope:?\s*[-•]\s*(.+?)(?:\n|$)", response, re.IGNORECASE | re.MULTILINE)
        out_scope = re.findall(r"Out of Scope:?\s*[-•]\s*(.+?)(?:\n|$)", response, re.IGNORECASE | re.MULTILINE)
        
        # Extract assumptions
        assumptions = re.findall(r"Assumption:?\s*[-•]\s*(.+?)(?:\n|$)", response, re.IGNORECASE | re.MULTILINE)
        
        content = f"""## System Purpose
{purpose}

## System Boundaries
### In Scope
{chr(10).join(f'- {item}' for item in in_scope)}

### Out of Scope
{chr(10).join(f'- {item}' for item in out_scope)}

## Key Assumptions
{chr(10).join(f'- {item}' for item in assumptions)}
"""
        
        return self.create_text(content, "markdown")
    
    def _parse_losses(self, response: str) -> List[Dict[str, Any]]:
        """Parse losses from response"""
        losses = []
        
        # Look for patterns like L-1:, L-2:, etc.
        loss_pattern = r"(L-\d+):?\s*(.+?)(?=L-\d+:|$)"
        matches = re.findall(loss_pattern, response, re.DOTALL)
        
        for loss_id, content in matches:
            # Extract description
            desc_match = re.search(r"(.+?)(?:Type:|Stakeholders:|Severity:|$)", content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else content.strip()
            
            # Extract type
            type_match = re.search(r"Type:?\s*(.+?)(?:Stakeholders:|Severity:|$)", content, re.IGNORECASE)
            loss_type = type_match.group(1).strip() if type_match else "Operational"
            
            # Extract stakeholders
            stake_match = re.search(r"Stakeholders:?\s*(.+?)(?:Severity:|$)", content, re.IGNORECASE)
            stakeholders = [s.strip() for s in stake_match.group(1).split(",")] if stake_match else []
            
            # Extract severity
            sev_match = re.search(r"Severity:?\s*(\w+)", content, re.IGNORECASE)
            severity = sev_match.group(1).strip() if sev_match else "High"
            
            losses.append({
                "id": loss_id,
                "description": description,
                "type": loss_type,
                "stakeholders": stakeholders,
                "severity": severity
            })
        
        return losses
    
    def _parse_hazards(self, response: str) -> List[Dict[str, Any]]:
        """Parse hazards from response"""
        hazards = []
        
        # Look for patterns like H-1:, H-2:, etc.
        hazard_pattern = r"(H-\d+):?\s*(.+?)(?=H-\d+:|$)"
        matches = re.findall(hazard_pattern, response, re.DOTALL)
        
        for hazard_id, content in matches:
            # Extract description and system state
            desc_match = re.search(r"(.+?)(?:that could lead to|System State:|Linked Losses:|$)", content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else content.strip()
            
            # Extract system state
            state_match = re.search(r"System State:?\s*(.+?)(?:Linked Losses:|$)", content, re.IGNORECASE)
            system_state = state_match.group(1).strip() if state_match else description
            
            # Extract linked losses
            losses_match = re.search(r"Linked Losses:?\s*(.+?)$", content, re.IGNORECASE)
            linked_losses = [l.strip() for l in losses_match.group(1).split(",")] if losses_match else []
            
            hazards.append({
                "id": hazard_id,
                "description": description,
                "system_state": system_state,
                "linked_losses": linked_losses
            })
        
        return hazards
    
    def _parse_constraints(self, response: str) -> List[Dict[str, Any]]:
        """Parse security constraints from response"""
        constraints = []
        
        # Look for patterns like SC-1:, SC-2:, etc.
        constraint_pattern = r"(SC-\d+):?\s*(.+?)(?=SC-\d+:|$)"
        matches = re.findall(constraint_pattern, response, re.DOTALL)
        
        for const_id, content in matches:
            constraints.append({
                "id": const_id,
                "description": content.strip(),
                "type": "Preventive",
                "related_hazards": []  # Could extract if mentioned
            })
        
        return constraints
    
    def _parse_control_structure(self, response: str) -> Dict[str, Any]:
        """Parse control structure into nodes and edges"""
        nodes = []
        edges = []
        
        # Extract controllers/processes
        controller_pattern = r"Controller:?\s*(.+?)(?:Controlled Process:|Control Actions:|$)"
        controllers = re.findall(controller_pattern, response, re.IGNORECASE | re.MULTILINE)
        
        for i, controller in enumerate(controllers):
            nodes.append({
                "id": f"controller_{i}",
                "label": controller.strip(),
                "type": "controller",
                "position": {"x": 100 + i * 200, "y": 100}
            })
        
        # Extract control actions
        action_pattern = r"(CA-\d+):?\s*(.+?)→(.+?)→(.+?)(?:\n|$)"
        actions = re.findall(action_pattern, response, re.MULTILINE)
        
        for action_id, controller, action, process in actions:
            # Find or create nodes
            controller_node = next((n for n in nodes if n["label"] == controller.strip()), None)
            if not controller_node:
                controller_node = {
                    "id": f"node_{len(nodes)}",
                    "label": controller.strip(),
                    "type": "controller"
                }
                nodes.append(controller_node)
            
            process_node = next((n for n in nodes if n["label"] == process.strip()), None)
            if not process_node:
                process_node = {
                    "id": f"node_{len(nodes)}",
                    "label": process.strip(),
                    "type": "process"
                }
                nodes.append(process_node)
            
            edges.append({
                "id": action_id,
                "source": controller_node["id"],
                "target": process_node["id"],
                "label": action.strip(),
                "type": "control"
            })
        
        # Extract feedback loops
        feedback_pattern = r"(FB-\d+):?\s*(.+?)→(.+?)→(.+?)(?:\n|$)"
        feedbacks = re.findall(feedback_pattern, response, re.MULTILINE)
        
        for fb_id, source, info, dest in feedbacks:
            source_node = next((n for n in nodes if n["label"] == source.strip()), None)
            dest_node = next((n for n in nodes if n["label"] == dest.strip()), None)
            
            if source_node and dest_node:
                edges.append({
                    "id": fb_id,
                    "source": source_node["id"],
                    "target": dest_node["id"],
                    "label": info.strip(),
                    "type": "feedback"
                })
        
        return {"nodes": nodes, "edges": edges}
    
    def _parse_control_actions(self, response: str) -> List[Dict[str, Any]]:
        """Parse control actions from response"""
        actions = []
        
        # Pattern: CA-X: Controller → Action → Process
        action_pattern = r"(CA-\d+):?\s*(.+?)→(.+?)→(.+?)(?:\n|Type:|$)"
        matches = re.findall(action_pattern, response, re.MULTILINE)
        
        for action_id, controller, action, process in matches:
            actions.append({
                "id": action_id,
                "controller": controller.strip(),
                "action": action.strip(),
                "controlled_process": process.strip(),
                "type": "Command"
            })
        
        return actions
    
    def _parse_feedback_loops(self, response: str) -> List[Dict[str, Any]]:
        """Parse feedback loops from response"""
        feedbacks = []
        
        # Pattern: FB-X: Source → Information → Destination
        feedback_pattern = r"(FB-\d+):?\s*(.+?)→(.+?)→(.+?)(?:\n|Purpose:|$)"
        matches = re.findall(feedback_pattern, response, re.MULTILINE)
        
        for fb_id, source, info, dest in matches:
            feedbacks.append({
                "id": fb_id,
                "source": source.strip(),
                "information": info.strip(),
                "destination": dest.strip(),
                "purpose": "Monitoring and control"
            })
        
        return feedbacks
    
    def _parse_ucas(self, response: str) -> List[Dict[str, Any]]:
        """Parse unsafe control actions from response"""
        ucas = []
        
        # Pattern for UCAs
        uca_pattern = r"(UCA-\d+):?\s*(.+?)(?=UCA-\d+:|$)"
        matches = re.findall(uca_pattern, response, re.DOTALL)
        
        for uca_id, content in matches:
            # Extract control action
            ca_match = re.search(r"Control Action:?\s*(.+?)(?:Type:|Context:|$)", content, re.IGNORECASE)
            control_action = ca_match.group(1).strip() if ca_match else ""
            
            # Extract type
            type_match = re.search(r"Type:?\s*(.+?)(?:Context:|Hazards:|$)", content, re.IGNORECASE)
            uca_type = type_match.group(1).strip() if type_match else "Not Provided"
            
            # Extract context
            context_match = re.search(r"Context:?\s*(.+?)(?:Hazards:|STRIDE:|$)", content, re.IGNORECASE)
            context = context_match.group(1).strip() if context_match else ""
            
            # Extract linked hazards
            hazards_match = re.search(r"Hazards:?\s*(.+?)(?:STRIDE:|$)", content, re.IGNORECASE)
            linked_hazards = [h.strip() for h in hazards_match.group(1).split(",")] if hazards_match else []
            
            # Extract STRIDE categories
            stride_match = re.search(r"STRIDE:?\s*(.+?)$", content, re.IGNORECASE)
            stride_categories = [s.strip() for s in stride_match.group(1).split(",")] if stride_match else []
            
            ucas.append({
                "id": uca_id,
                "control_action": control_action,
                "type": uca_type,
                "context": context,
                "linked_hazards": linked_hazards,
                "stride_categories": stride_categories
            })
        
        return ucas
    
    def _parse_causal_scenarios(self, response: str) -> List[Dict[str, Any]]:
        """Parse causal scenarios from response"""
        scenarios = []
        
        # Pattern for scenarios
        scenario_pattern = r"(CS-\d+):?\s*(.+?)(?=CS-\d+:|$)"
        matches = re.findall(scenario_pattern, response, re.DOTALL)
        
        for scenario_id, content in matches:
            # Extract UCA reference
            uca_match = re.search(r"UCA:?\s*(UCA-\d+)", content, re.IGNORECASE)
            uca_id = uca_match.group(1) if uca_match else ""
            
            # Extract description
            desc_match = re.search(r"Scenario:?\s*(.+?)(?:Causal Factors:|Attack:|$)", content, re.IGNORECASE)
            description = desc_match.group(1).strip() if desc_match else content.strip()
            
            # Extract causal factors
            factors_match = re.search(r"Causal Factors:?\s*(.+?)(?:Attack Complexity:|$)", content, re.IGNORECASE)
            causal_factors = [f.strip() for f in factors_match.group(1).split(";")] if factors_match else []
            
            # Extract complexity
            complexity_match = re.search(r"Attack Complexity:?\s*(\w+)", content, re.IGNORECASE)
            complexity = complexity_match.group(1) if complexity_match else "Medium"
            
            scenarios.append({
                "id": scenario_id,
                "uca_id": uca_id,
                "description": description,
                "causal_factors": causal_factors,
                "complexity": complexity
            })
        
        return scenarios
    
    def _parse_security_controls(self, response: str) -> List[Dict[str, Any]]:
        """Parse security controls from response"""
        controls = []
        
        # Pattern for controls
        control_pattern = r"(CTRL-\d+):?\s*(.+?)(?=CTRL-\d+:|$)"
        matches = re.findall(control_pattern, response, re.DOTALL)
        
        for control_id, content in matches:
            # Extract description
            desc_match = re.search(r"(.+?)(?:Type:|Priority:|$)", content, re.DOTALL)
            description = desc_match.group(1).strip() if desc_match else content.strip()
            
            # Extract type
            type_match = re.search(r"Type:?\s*(.+?)(?:Priority:|Related:|$)", content, re.IGNORECASE)
            control_type = type_match.group(1).strip() if type_match else "Preventive"
            
            # Extract priority
            priority_match = re.search(r"Priority:?\s*(\w+)", content, re.IGNORECASE)
            priority = priority_match.group(1).strip() if priority_match else "Important"
            
            # Extract related scenarios
            related_match = re.search(r"Related Scenarios:?\s*(.+?)$", content, re.IGNORECASE)
            related_scenarios = [s.strip() for s in related_match.group(1).split(",")] if related_match else []
            
            controls.append({
                "id": control_id,
                "description": description,
                "type": control_type,
                "priority": priority,
                "related_scenarios": related_scenarios
            })
        
        return controls
    
    def _extract_artifacts(self, sections: List[SectionResult]) -> List[Dict[str, Any]]:
        """Extract key artifacts for other agents to use"""
        artifacts = []
        
        for section in sections:
            if section.section_id == "control_structure" and section.status.value == "completed":
                artifacts.append({
                    "type": "control_structure",
                    "name": "System Control Structure",
                    "data": section.content
                })
            elif section.section_id == "hazards" and section.status.value == "completed":
                artifacts.append({
                    "type": "hazards",
                    "name": "Identified Hazards",
                    "data": section.content
                })
            elif section.section_id == "ucas" and section.status.value == "completed":
                artifacts.append({
                    "type": "unsafe_control_actions",
                    "name": "Unsafe Control Actions",
                    "data": section.content
                })
        
        return artifacts