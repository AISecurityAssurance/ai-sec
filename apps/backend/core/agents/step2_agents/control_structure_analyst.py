"""
Control Structure Analyst Agent for Step 2 STPA-Sec
Identifies controllers, controlled processes, and their relationships.
"""
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime

from .base_step2 import BaseStep2Agent, AgentResult
from .db_compat import Step2DBCompat
from .component_registry import ComponentRegistry
from core.agents.step1_agents.base_step1 import CognitiveStyle
from core.utils.json_parser import parse_llm_json


class ControlStructureAnalystAgent(BaseStep2Agent):
    """
    Identifies system components (controllers and controlled processes)
    and their hierarchical relationships.
    """
    
    async def analyze(self, step1_analysis_id: str, step2_analysis_id: str, **kwargs) -> AgentResult:
        """Identify control structure components."""
        start_time = datetime.now()
        
        # Get or create component registry
        registry = kwargs.get('component_registry')
        if registry is None:
            registry = ComponentRegistry()
        
        # Load Step 1 results
        step1_results = await self.load_step1_results(step1_analysis_id)
        
        # Build prompt for control structure identification
        prompt = self._build_control_structure_prompt(step1_results, kwargs.get('previous_results', {}))
        
        # Get LLM response with retry logic
        messages = [
            {"role": "system", "content": "You are an expert systems security analyst specializing in STPA-Sec control structure analysis. You MUST respond with raw JSON only. Do NOT use markdown formatting, code blocks, or backticks. Start your response directly with { and end with }. No ```json tags."},
            {"role": "user", "content": prompt}
        ]
        
        # Use the new retry method from base class
        response_text = await self.query_llm_with_retry(messages, temperature=0.7, max_tokens=4000)
        
        # Parse response
        components = self._parse_control_structure(response_text, step1_results)
        
        # Store in database and register in component registry
        await self._store_components(step2_analysis_id, components, registry)
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AgentResult(
            agent_type="control_structure_analyst",
            success=True,
            data={
                'components': components,
                'summary': self._generate_summary(components),
                'component_registry': registry
            },
            execution_time_ms=execution_time,
            metadata={
                'cognitive_style': self.cognitive_style.value,
                'component_count': len(components['controllers']) + len(components['controlled_processes']),
                'hierarchy_levels': components.get('hierarchy_depth', 0)
            }
        )
        
    def _build_control_structure_prompt(self, step1_results: Dict[str, Any], previous_results: Dict[str, Any] = None) -> str:
        """Build prompt for control structure identification."""
        base_prompt = self.format_control_structure_prompt(step1_results)
        
        # Apply expert refinement if available
        if previous_results:
            base_prompt = self.apply_expert_refinement(base_prompt, previous_results)
        
        cognitive_prompts = {
            CognitiveStyle.INTUITIVE: """
Focus on natural control relationships and decision-making flows.
Think about WHO makes decisions and WHO carries them out.
Consider both formal and informal control structures.""",
            CognitiveStyle.SYSTEMATIC: """
Systematically decompose the system into control layers.
Identify precise control interfaces and protocols.
Map exact command/response patterns.""",
            CognitiveStyle.TECHNICAL: """
Focus on technical control mechanisms and implementations.
Identify specific control protocols, APIs, and interfaces.
Consider automated vs manual control points.""",
            CognitiveStyle.SYSTEMATIC: """
Create a complete hierarchical breakdown of control.
Ensure all system functions have associated controllers.
Map control responsibilities comprehensively.""",
            CognitiveStyle.CREATIVE: """
Think beyond obvious control structures.
Consider emergent control patterns and edge cases.
Identify potential control conflicts or gaps.""",
            CognitiveStyle.BALANCED: """
Provide a comprehensive control structure analysis.
Balance technical accuracy with practical understanding.
Consider both normal and exceptional control flows."""
        }
        
        style_prompt = cognitive_prompts.get(self.cognitive_style, cognitive_prompts[CognitiveStyle.BALANCED])
        
        prompt = f"""{base_prompt}

## Task: Identify Control Structure Components

{style_prompt}

For this system, identify:

1. **Controllers**: Components that make decisions and issue commands
   - Name and unique identifier (CTRL-X)
   - What they control
   - Their authority level
   - Source (from stakeholders, system description, or inferred)

2. **Controlled Processes**: Components that execute actions
   - Name and unique identifier (PROC-X)  
   - What controls them
   - What they do
   - Their criticality level

3. **Dual-Role Components**: Components that both control and are controlled
   - Name and unique identifier (DUAL-X)
   - What they control
   - What controls them
   - Why they have both roles

4. **Control Hierarchy**: Parent-child relationships
   - Which controllers supervise other controllers
   - Delegation patterns
   - Coordination requirements

Provide your response in the following JSON format:
{{
    "controllers": [
        {{
            "identifier": "CTRL-1",
            "name": "Controller Name",
            "description": "What this controller does",
            "controls": ["List of what it controls"],
            "authority_level": "high/medium/low",
            "source": "stakeholder_analysis/system_description/inferred",
            "abstraction_level": "service/subsystem/component"
        }}
    ],
    "controlled_processes": [
        {{
            "identifier": "PROC-1",
            "name": "Process Name",
            "description": "What this process does",
            "controlled_by": ["List of controllers"],
            "criticality": "critical/high/medium/low",
            "abstraction_level": "service/subsystem/component"
        }}
    ],
    "dual_role_components": [
        {{
            "identifier": "DUAL-1",
            "name": "Component Name",
            "description": "What this component does",
            "controls": ["What it controls"],
            "controlled_by": ["What controls it"],
            "rationale": "Why it has both roles",
            "abstraction_level": "service/subsystem/component"
        }}
    ],
    "control_hierarchy": [
        {{
            "parent": "CTRL-X",
            "child": "CTRL-Y",
            "relationship_type": "supervises/coordinates/delegates",
            "description": "Nature of the relationship"
        }}
    ],
    "analysis_notes": "Key insights about the control structure"
}}

Focus on security-relevant control relationships.
Ensure all critical functions have associated controllers.
Identify potential control gaps or conflicts.

CRITICAL: Return ONLY valid JSON. Do NOT wrap in markdown code blocks or use backticks.
Start your response with {{ and end with }}.
Ensure all string values properly escape newlines and quotes.
"""
        
        return prompt
        
    def _parse_control_structure(self, response: str, step1_results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured components."""
        try:
            # Parse JSON response
            data = parse_llm_json(response)
            
            # Add metadata and validation
            components = {
                'controllers': data.get('controllers', []),
                'controlled_processes': data.get('controlled_processes', []),
                'dual_role_components': data.get('dual_role_components', []),
                'control_hierarchy': data.get('control_hierarchy', []),
                'analysis_notes': data.get('analysis_notes', ''),
                'hierarchy_depth': self._calculate_hierarchy_depth(data.get('control_hierarchy', []))
            }
            
            # Validate and enhance components
            self._validate_components(components)
            self._enhance_with_step1_context(components, step1_results)
            
            return components
            
        except Exception as e:
            # Fallback structure
            return {
                'controllers': [
                    {
                        'identifier': 'CTRL-1',
                        'name': 'System Administrator',
                        'description': 'Overall system control and configuration',
                        'controls': ['System configuration', 'Access control'],
                        'authority_level': 'high',
                        'source': 'inferred',
                        'abstraction_level': 'service'
                    }
                ],
                'controlled_processes': [
                    {
                        'identifier': 'PROC-1',
                        'name': 'Core System Process',
                        'description': 'Main system functionality',
                        'controlled_by': ['CTRL-1'],
                        'criticality': 'critical',
                        'abstraction_level': 'service'
                    }
                ],
                'dual_role_components': [],
                'control_hierarchy': [],
                'analysis_notes': f'Basic structure inferred. Parse error: {str(e)}',
                'hierarchy_depth': 1
            }
            
    def _calculate_hierarchy_depth(self, hierarchy: List[Dict[str, Any]]) -> int:
        """Calculate the depth of the control hierarchy."""
        if not hierarchy:
            return 1
            
        # Build parent-child map
        children_map = {}
        all_nodes = set()
        
        for rel in hierarchy:
            parent = rel.get('parent')
            child = rel.get('child')
            if parent and child:
                all_nodes.add(parent)
                all_nodes.add(child)
                if parent not in children_map:
                    children_map[parent] = []
                children_map[parent].append(child)
                
        # Find roots (nodes with no parents)
        roots = all_nodes - set(child for children in children_map.values() for child in children)
        
        # Calculate max depth from each root
        def get_depth(node, visited=None):
            if visited is None:
                visited = set()
            if node in visited:
                return 0
            visited.add(node)
            
            if node not in children_map:
                return 1
                
            return 1 + max(get_depth(child, visited) for child in children_map[node])
            
        if roots:
            return max(get_depth(root) for root in roots)
        return 1
        
    def _validate_components(self, components: Dict[str, Any]) -> None:
        """Validate component structure and relationships."""
        # Ensure all components have required fields
        for controller in components['controllers']:
            controller.setdefault('identifier', f"CTRL-{uuid.uuid4().hex[:8]}")
            controller.setdefault('authority_level', 'medium')
            controller.setdefault('source', 'inferred')
            controller.setdefault('abstraction_level', 'service')
            
        for process in components['controlled_processes']:
            process.setdefault('identifier', f"PROC-{uuid.uuid4().hex[:8]}")
            process.setdefault('criticality', 'medium')
            process.setdefault('abstraction_level', 'service')
            
        for dual in components['dual_role_components']:
            dual.setdefault('identifier', f"DUAL-{uuid.uuid4().hex[:8]}")
            dual.setdefault('abstraction_level', 'service')
            
    def _enhance_with_step1_context(self, components: Dict[str, Any], step1_results: Dict[str, Any]) -> None:
        """Enhance components with context from Step 1."""
        # Map stakeholders to potential controllers
        stakeholder_map = {s['name']: s for s in step1_results.get('stakeholders', [])}
        
        for controller in components['controllers']:
            # Check if controller matches a stakeholder
            for stakeholder_name, stakeholder in stakeholder_map.items():
                if (stakeholder_name.lower() in controller['name'].lower() or 
                    controller['name'].lower() in stakeholder_name.lower()):
                    controller['stakeholder_link'] = stakeholder['id']
                    controller['trust_level'] = stakeholder.get('trust_level', 'medium')
                    
    async def _store_components(self, step2_analysis_id: str, components: Dict[str, Any], registry: ComponentRegistry) -> None:
        """Store components in database and register in component registry."""
        # Create compatibility layer
        db_compat = Step2DBCompat(self.db_connection)
        
        # Store controllers
        for controller in components['controllers']:
            try:
                # Register in component registry
                registry.register_component(
                    identifier=controller['identifier'],
                    name=controller['name'],
                    comp_type='controller',
                    description=controller.get('description', ''),
                    source='control_structure_analyst',
                    authority_level=controller.get('authority_level'),
                    controls=controller.get('controls', []),
                    abstraction_level=controller.get('abstraction_level', 'service')
                )
                
                # Store in database
                await db_compat.insert_component(
                    component_id=str(uuid.uuid4()),
                    analysis_id=step2_analysis_id,
                    identifier=controller['identifier'],
                    name=controller['name'],
                    component_type='controller',
                    description=controller.get('description', ''),
                    abstraction_level=controller.get('abstraction_level', 'service'),
                    source=controller.get('source', 'inferred'),
                    metadata={
                        'authority_level': controller.get('authority_level'),
                        'controls': controller.get('controls', []),
                        'stakeholder_link': controller.get('stakeholder_link'),
                        'trust_level': controller.get('trust_level')
                    }
                )
            except Exception as e:
                self.logger.error(f"Error storing controller {controller['name']}: {e}")
                raise
            
        # Store controlled processes
        for process in components['controlled_processes']:
            try:
                # Register in component registry
                registry.register_component(
                    identifier=process['identifier'],
                    name=process['name'],
                    comp_type='process',
                    description=process.get('description', ''),
                    source='control_structure_analyst',
                    criticality=process.get('criticality'),
                    controlled_by=process.get('controlled_by', []),
                    abstraction_level=process.get('abstraction_level', 'service')
                )
                
                # Store in database
                await db_compat.insert_component(
                    component_id=str(uuid.uuid4()),
                    analysis_id=step2_analysis_id,
                    identifier=process['identifier'],
                    name=process['name'],
                    component_type='controlled_process',
                    description=process.get('description', ''),
                    abstraction_level=process.get('abstraction_level', 'service'),
                    source='system_description',
                    metadata={
                        'criticality': process.get('criticality'),
                        'controlled_by': process.get('controlled_by', [])
                    }
                )
            except Exception as e:
                self.logger.error(f"Error storing process {process['name']}: {e}")
                raise
            
        # Store dual-role components
        for dual in components['dual_role_components']:
            try:
                # Register in component registry
                registry.register_component(
                    identifier=dual['identifier'],
                    name=dual['name'],
                    comp_type='dual-role',
                    description=dual.get('description', ''),
                    source='control_structure_analyst',
                    controls=dual.get('controls', []),
                    controlled_by=dual.get('controlled_by', []),
                    rationale=dual.get('rationale', ''),
                    abstraction_level=dual.get('abstraction_level', 'service')
                )
                
                # Store in database
                await db_compat.insert_component(
                    component_id=str(uuid.uuid4()),
                    analysis_id=step2_analysis_id,
                    identifier=dual['identifier'],
                    name=dual['name'],
                    component_type='both',
                    description=dual.get('description', ''),
                    abstraction_level=dual.get('abstraction_level', 'service'),
                    source='inferred',
                    metadata={
                        'controls': dual.get('controls', []),
                        'controlled_by': dual.get('controlled_by', []),
                        'rationale': dual.get('rationale', '')
                    }
                )
            except Exception as e:
                self.logger.error(f"Error storing dual component {dual['name']}: {e}")
                raise
            
        # Store hierarchy relationships
        for rel in components['control_hierarchy']:
            # Register hierarchy in component registry
            registry.add_reference(rel['parent'], rel['child'])
            
            # Need to look up component IDs by identifier
            parent_id = await self._get_component_id(step2_analysis_id, rel['parent'])
            child_id = await self._get_component_id(step2_analysis_id, rel['child'])
            
            if parent_id and child_id:
                await self.db_connection.execute(
                    """
                    INSERT INTO control_hierarchies 
                    (id, analysis_id, parent_component_id, child_component_id, 
                     relationship_type, description)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    ON CONFLICT (parent_component_id, child_component_id) 
                    DO UPDATE SET
                        relationship_type = EXCLUDED.relationship_type,
                        description = EXCLUDED.description
                    """,
                    str(uuid.uuid4()),
                    step2_analysis_id,
                    parent_id,
                    child_id,
                    rel.get('relationship_type', 'supervises'),
                    rel.get('description', '')
                )
                
    async def _get_component_id(self, analysis_id: str, identifier: str) -> Optional[str]:
        """Get component ID by identifier."""
        result = await self.db_connection.fetchrow(
            "SELECT id FROM system_components WHERE analysis_id = $1 AND identifier = $2",
            analysis_id, identifier
        )
        return result['id'] if result else None
        
    def _generate_summary(self, components: Dict[str, Any]) -> str:
        """Generate summary of control structure."""
        controller_count = len(components['controllers'])
        process_count = len(components['controlled_processes'])
        dual_count = len(components['dual_role_components'])
        hierarchy_count = len(components['control_hierarchy'])
        
        summary = f"""Identified {controller_count} controllers, {process_count} controlled processes, and {dual_count} dual-role components.
        
Control hierarchy has {components['hierarchy_depth']} levels with {hierarchy_count} relationships.
        
{components.get('analysis_notes', '')}"""
        
        return summary
