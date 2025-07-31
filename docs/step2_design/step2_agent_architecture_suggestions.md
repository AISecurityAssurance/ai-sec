~"""
STPA-Sec Step 2 Agent Architecture
Designed for formal verification readiness and code-aware analysis
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import asyncio
import json
from pathlib import Path

@dataclass
class Step2Context:
    """Context shared across Step 2 agents"""
    step1_results: Dict[str, Any]
    system_description: str
    codebase_path: Optional[str] = None
    abstraction_level: str = "service"  # service, class, method
    include_state_machines: bool = True
    formal_verification_mode: bool = False

@dataclass  
class ControlStructureComponent:
    """Represents a component in the control structure"""
    identifier: str
    name: str
    component_type: str  # controller, controlled_process, hybrid
    authority_level: str
    trust_level: str
    has_state_machine: bool = False
    code_location: Optional[Dict] = None
    properties: Optional[Dict] = None

@dataclass
class ControlAction:
    """Represents a control action between components"""
    identifier: str
    name: str
    controller_id: str
    controlled_process_id: str
    action_type: str
    timing_type: str
    triggers_state_transition: bool = False
    requires_authentication: bool = False
    requires_authorization: bool = False
    implementation_details: Optional[Dict] = None

@dataclass
class StateMachineDefinition:
    """Represents a state machine for formal verification"""
    name: str
    component_id: str
    machine_type: str
    states: List[Dict]
    transitions: List[Dict]
    initial_state: str
    security_properties: List[Dict]
    invariants: List[Dict]

class BaseStep2Agent(ABC):
    """Base class for Step 2 agents"""
    
    def __init__(self, db_connection, llm_client):
        self.db = db_connection
        self.llm = llm_client
        
    @abstractmethod
    async def analyze(self, context: Step2Context) -> Dict[str, Any]:
        """Perform the specific Step 2 analysis"""
        pass
        
    async def save_results(self, analysis_id: str, results: Dict[str, Any]):
        """Save results to database"""
        # Implementation depends on specific agent type
        pass

class CodebaseAnalysisAgent(BaseStep2Agent):
    """Analyzes codebase to extract components and relationships"""
    
    async def analyze(self, context: Step2Context) -> Dict[str, Any]:
        """Extract components from codebase if available"""
        
        if not context.codebase_path:
            return {"codebase_analysis": None, "code_aware": False}
            
        codebase_path = Path(context.codebase_path)
        if not codebase_path.exists():
            return {"codebase_analysis": None, "code_aware": False}
            
        # Basic static analysis - can be enhanced with more sophisticated tools
        discovered_components = await self._discover_components(codebase_path, context.abstraction_level)
        discovered_relationships = await self._discover_relationships(codebase_path, discovered_components)
        security_annotations = await self._find_security_annotations(codebase_path)
        state_machines = await self._discover_state_machines(codebase_path)
        
        return {
            "codebase_analysis": {
                "discovered_components": discovered_components,
                "discovered_relationships": discovered_relationships, 
                "security_annotations": security_annotations,
                "state_machines": state_machines
            },
            "code_aware": True
        }
    
    async def _discover_components(self, codebase_path: Path, abstraction_level: str) -> List[Dict]:
        """Discover components based on abstraction level"""
        # Implementation would use AST parsing, pattern matching, etc.
        # For now, return structure that agents can use
        return [
            {
                "name": "AuthService",
                "type": "service",
                "file_path": "src/auth/AuthService.java",
                "likely_controller": True,
                "security_related": True
            },
            # ... more components
        ]
    
    async def _discover_relationships(self, codebase_path: Path, components: List[Dict]) -> List[Dict]:
        """Discover relationships between components"""
        return [
            {
                "from": "AuthController", 
                "to": "AuthService",
                "relationship_type": "uses",
                "interaction_pattern": "method_call"
            }
            # ... more relationships
        ]
    
    async def _find_security_annotations(self, codebase_path: Path) -> Dict:
        """Find security-related annotations and patterns"""
        return {
            "authentication_annotations": ["@Authenticated", "@RequiresAuth"],
            "authorization_annotations": ["@Authorized", "@RolesAllowed"],
            "state_machine_annotations": ["@StateMachine", "@State", "@Transition"]
        }
    
    async def _discover_state_machines(self, codebase_path: Path) -> List[Dict]:
        """Discover state machine implementations"""
        return [
            {
                "name": "AuthStateMachine",
                "component": "AuthService", 
                "framework": "Spring State Machine",
                "config_location": "auth-state-machine.xml"
            }
        ]

class ControlStructureAnalystAgent(BaseStep2Agent):
    """Identifies controllers and controlled processes from Step 1 results"""
    
    async def analyze(self, context: Step2Context) -> Dict[str, Any]:
        """Extract control structure from Step 1 results and optional codebase"""
        
        # Extract from Step 1 stakeholder analysis
        components_from_step1 = await self._extract_from_stakeholders(context.step1_results)
        
        # Extract from system description
        components_from_description = await self._extract_from_description(context.system_description)
        
        # Enhance with codebase analysis if available
        if context.codebase_path:
            codebase_results = await CodebaseAnalysisAgent(self.db, self.llm).analyze(context)
            components_from_code = codebase_results.get("codebase_analysis", {}).get("discovered_components", [])
        else:
            components_from_code = []
        
        # Synthesize and validate components
        synthesized_components = await self._synthesize_components(
            components_from_step1, 
            components_from_description,
            components_from_code,
            context
        )
        
        return {
            "system_components": synthesized_components,
            "component_count": len(synthesized_components),
            "controller_count": len([c for c in synthesized_components if c.component_type in ['controller', 'hybrid']]),
            "controlled_process_count": len([c for c in synthesized_components if c.component_type in ['controlled_process', 'hybrid']])
        }
    
    async def _extract_from_stakeholders(self, step1_results: Dict) -> List[ControlStructureComponent]:
        """Extract components from Step 1 stakeholder analysis"""
        components = []
        
        stakeholders = step1_results.get('stakeholder_analyst', {}).get('stakeholders', [])
        for stakeholder in stakeholders:
            if stakeholder.get('stakeholder_type') in ['operator', 'administrator']:
                components.append(ControlStructureComponent(
                    identifier=f"C-{len(components)+1}",
                    name=stakeholder['name'],
                    component_type='controller',
                    authority_level='administrative' if 'admin' in stakeholder['name'].lower() else 'system',
                    trust_level='trusted'
                ))
        
        return components
    
    async def _extract_from_description(self, system_description: str) -> List[ControlStructureComponent]:
        """Use LLM to extract components from system description"""
        
        prompt = f"""
        You are analyzing a system for STPA-Sec Step 2 control structure identification.
        
        System Description: {system_description}
        
        Identify:
        1. Controllers: Components that make decisions and issue commands
        2. Controlled Processes: Components that execute actions based on commands
        3. Hybrid Components: Components that both control and are controlled
        
        For each component, determine:
        - Authority level (none, local, system, administrative, root)
        - Trust level (untrusted, partially_trusted, trusted, critical)
        - Whether it likely has state machine behavior
        
        Focus on architectural-level components, not implementation details.
        
        Return JSON format with components array.
        """
        
        response = await self.llm.generate(prompt)
        # Parse and validate response
        return self._parse_component_response(response)
    
    async def _synthesize_components(self, step1_comps, desc_comps, code_comps, context) -> List[ControlStructureComponent]:
        """Synthesize components from all sources"""
        # Implementation would merge and deduplicate components
        # Priority: Step 1 > Code > Description
        synthesized = []
        
        # Add Step 1 components (highest priority)
        synthesized.extend(step1_comps)
        
        # Add description components not already covered
        for comp in desc_comps:
            if not any(existing.name == comp.name for existing in synthesized):
                synthesized.append(comp)
        
        # Enhance with code information
        for comp in synthesized:
            code_match = next((c for c in code_comps if c.get('name') == comp.name), None)
            if code_match:
                comp.code_location = {
                    "file_path": code_match.get('file_path'),
                    "class_name": code_match.get('name'),
                    "security_related": code_match.get('security_related', False)
                }
        
        return synthesized

class ControlActionMappingAgent(BaseStep2Agent):
    """Maps control actions between components"""
    
    async def analyze(self, context: Step2Context) -> Dict[str, Any]:
        """Identify control actions between components"""
        
        # Get components from previous agent
        components = await self._get_components(context)
        
        # Generate control actions
        control_actions = await self._generate_control_actions(components, context)
        
        # Enhance with security requirements
        enhanced_actions = await self._add_security_requirements(control_actions, context)
        
        return {
            "control_actions": enhanced_actions,
            "control_action_count": len(enhanced_actions)
        }
    
    async def _generate_control_actions(self, components: List[ControlStructureComponent], context: Step2Context) -> List[ControlAction]:
        """Generate control actions between components using LLM"""
        
        controllers = [c for c in components if c.component_type in ['controller', 'hybrid']]
        processes = [c for c in components if c.component_type in ['controlled_process', 'hybrid']]
        
        prompt = f"""
        You are identifying control actions for STPA-Sec Step 2 analysis.
        
        System: {context.system_description}
        
        Controllers: {[c.name for c in controllers]}
        Controlled Processes: {[c.name for c in processes]}
        
        For each meaningful controller-process relationship, identify:
        1. What commands/decisions the controller sends
        2. Action type (command, query, configuration, authentication, authorization)
        3. Timing requirements (synchronous, asynchronous, periodic, event_driven)
        4. Whether it triggers state transitions
        5. Security requirements
        
        Focus on control relationships that could affect system security or safety.
        Return JSON with control_actions array.
        """
        
        response = await self.llm.generate(prompt)
        return self._parse_control_actions(response, components)

class FeedbackAnalysisAgent(BaseStep2Agent):
    """Identifies feedback mechanisms"""
    
    async def analyze(self, context: Step2Context) -> Dict[str, Any]:
        """Identify feedback mechanisms between processes and controllers"""
        
        # Implementation similar to ControlActionMappingAgent
        # but focusing on information flows back to controllers
        pass

class TrustBoundaryAgent(BaseStep2Agent):
    """Identifies trust boundaries and security perimeters"""
    
    async def analyze(self, context: Step2Context) -> Dict[str, Any]:
        """Identify trust boundaries from Step 1 adversary analysis and control structure"""
        
        # Get adversary profiles from Step 1
        adversaries = context.step1_results.get('stakeholder_analyst', {}).get('adversaries', [])
        
        # Get components 
        components = await self._get_components(context)
        
        # Identify boundaries based on adversary capabilities and component relationships
        trust_boundaries = await self._identify_trust_boundaries(components, adversaries, context)
        
        return {
            "trust_boundaries": trust_boundaries,
            "boundary_count": len(trust_boundaries)
        }

class StateMachineAnalysisAgent(BaseStep2Agent):
    """Analyzes and extracts state machine definitions for formal verification"""
    
    async def analyze(self, context: Step2Context) -> Dict[str, Any]:
        """Extract state machine definitions for components that need them"""
        
        if not context.include_state_machines:
            return {"state_machines": [], "formal_verification_ready": False}
        
        # Get components that likely have state machines
        components = await self._get_components(context)
        stateful_components = [c for c in components if c.has_state_machine or self._likely_stateful(c)]
        
        state_machines = []
        for component in stateful_components:
            sm_def = await self._extract_state_machine(component, context)
            if sm_def:
                state_machines.append(sm_def)
        
        # Validate for formal verification readiness
        verification_ready = await self._validate_for_formal_verification(state_machines)
        
        return {
            "state_machines": state_machines,
            "stateful_component_count": len(stateful_components),
            "formal_verification_ready": verification_ready
        }
    
    def _likely_stateful(self, component: ControlStructureComponent) -> bool:
        """Determine if component likely has state machine behavior"""
        stateful_keywords = ['auth', 'session', 'workflow', 'process', 'transaction']
        return any(keyword in component.name.lower() for keyword in stateful_keywords)
    
    async def _extract_state_machine(self, component: ControlStructureComponent, context: Step2Context) -> Optional[StateMachineDefinition]:
        """Extract state machine definition for a component"""
        
        prompt = f"""
        You are extracting state machine definition for formal verification in STPA-Sec.
        
        Component: {component.name} (Type: {component.component_type})
        System Context: {context.system_description}
        
        Define a state machine with:
        1. States (including security properties of each state)
        2. Transitions (with guards/conditions)
        3. Initial state
        4. Security invariants (properties that must always hold)
        5. Authentication/authorization requirements for transitions
        
        Focus on security-relevant state transitions.
        Return JSON format with states, transitions, initial_state, security_properties arrays.
        """
        
        response = await self.llm.generate(prompt)
        return self._parse_state_machine(response, component)
    
    async def _validate_for_formal_verification(self, state_machines: List[StateMachineDefinition]) -> bool:
        """Check if state machines are suitable for formal verification"""
        
        for sm in state_machines:
            # Check for required formal verification elements
            if not sm.security_properties or not sm.invariants:
                return False
            
            # Check for complete mediation (every transition has security check)
            for transition in sm.transitions:
                if not transition.get('guards') and not transition.get('security_check'):
                    return False
        
        return True

class Step2Coordinator:
    """Orchestrates all Step 2 agents"""
    
    def __init__(self, db_connection, llm_client):
        self.db = db_connection
        self.llm = llm_client
        
        # Initialize agents
        self.agents = {
            'codebase_analysis': CodebaseAnalysisAgent(db_connection, llm_client),
            'control_structure': ControlStructureAnalystAgent(db_connection, llm_client), 
            'control_actions': ControlActionMappingAgent(db_connection, llm_client),
            'feedback_mechanisms': FeedbackAnalysisAgent(db_connection, llm_client),
            'trust_boundaries': TrustBoundaryAgent(db_connection, llm_client),
            'state_machines': StateMachineAnalysisAgent(db_connection, llm_client)
        }
    
    async def perform_step2_analysis(self, step1_analysis_id: str, context: Step2Context) -> Dict[str, Any]:
        """Perform complete Step 2 analysis"""
        
        # Create Step 2 analysis record
        step2_analysis_id = await self._create_step2_analysis(step1_analysis_id, context)
        
        results = {}
        
        # Phase 1: Optional codebase analysis
        if context.codebase_path:
            results['codebase_analysis'] = await self.agents['codebase_analysis'].analyze(context)
        
        # Phase 2: Core control structure
        results['control_structure'] = await self.agents['control_structure'].analyze(context)
        
        # Phase 3: Control actions and feedback (can run in parallel)
        control_actions_task = self.agents['control_actions'].analyze(context)
        feedback_task = self.agents['feedback_mechanisms'].analyze(context)
        
        results['control_actions'] = await control_actions_task
        results['feedback_mechanisms'] = await feedback_task
        
        # Phase 4: Security analysis
        results['trust_boundaries'] = await self.agents['trust_boundaries'].analyze(context)
        
        # Phase 5: State machine analysis (if requested)
        if context.include_state_machines:
            results['state_machines'] = await self.agents['state_machines'].analyze(context)
        
        # Phase 6: Save all results to database
        await self._save_all_results(step2_analysis_id, results)
        
        # Phase 7: Generate summary and validation
        summary = await self._generate_summary(results)
        
        return {
            'step2_analysis_id': step2_analysis_id,
            'results': results,
            'summary': summary
        }
    
    async def _create_step2_analysis(self, step1_analysis_id: str, context: Step2Context) -> str:
        """Create Step 2 analysis record in database"""
        # Implementation would create record in step2_analyses table
        pass
    
    async def _save_all_results(self, analysis_id: str, results: Dict[str, Any]):
        """Save all results to appropriate database tables"""
        # Implementation would save to all Step 2 tables
        pass
    
    async def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate analysis summary and quality metrics"""
        return {
            'total_components': results.get('control_structure', {}).get('component_count', 0),
            'total_control_actions': results.get('control_actions', {}).get('control_action_count', 0),
            'trust_boundaries': results.get('trust_boundaries', {}).get('boundary_count', 0),
            'state_machines': len(results.get('state_machines', {}).get('state_machines', [])),
            'formal_verification_ready': results.get('state_machines', {}).get('formal_verification_ready', False),
            'code_aware': results.get('codebase_analysis', {}).get('code_aware', False)
        }

# Example usage
async def example_step2_analysis():
    """Example of how to run Step 2 analysis"""
    
    # Mock database and LLM connections
    db_connection = None  # Your database connection
    llm_client = None     # Your LLM client
    
    # Create context
    context = Step2Context(
        step1_results={
            # Step 1 results from previous analysis
            'stakeholder_analyst': {
                'stakeholders': [
                    {'name': 'System Administrator', 'stakeholder_type': 'operator'},
                    {'name': 'End Users', 'stakeholder_type': 'user'}
                ],
                'adversaries': [
                    {'name': 'External Attacker', 'sophistication_level': 'advanced'}
                ]
            }
        },
        system_description="Digital banking platform with authentication and payment processing",
        codebase_path="/path/to/banking/codebase",
        abstraction_level="service",
        include_state_machines=True,
        formal_verification_mode=True
    )
    
    # Run analysis
    coordinator = Step2Coordinator(db_connection, llm_client)
    results = await coordinator.perform_step2_analysis("step1-analysis-id", context)
    
    return results~

