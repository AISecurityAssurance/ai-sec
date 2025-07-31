"""
Control Structure Analyst Agent for Step 2 STPA-Sec
Identifies controllers, controlled processes, and their relationships.
"""
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime

from .base_step2 import BaseStep2Agent
from core.types import CognitiveStyle, AgentResult
from core.utils import clean_json_string


class ControlStructureAnalystAgent(BaseStep2Agent):
    """
    Identifies system components (controllers and controlled processes)
    and their hierarchical relationships.
    """
    
    async def analyze(self, step1_analysis_id: str, step2_analysis_id: str, **kwargs) -> AgentResult:
        """Identify control structure components."""
        start_time = datetime.now()
        
        # Load Step 1 results
        step1_results = await self.load_step1_results(step1_analysis_id)
        
        # Build prompt for control structure identification
        prompt = self._build_control_structure_prompt(step1_results)
        
        # Get LLM response
        response = await self.model_provider.get_completion(prompt)
        
        # Parse response
        components = self._parse_control_structure(response, step1_results)
        
        # Store in database
        await self._store_components(step2_analysis_id, components)
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AgentResult(
            agent_type="control_structure_analyst",
            success=True,
            data={
                'components': components,
                'summary': self._generate_summary(components)
            },
            execution_time_ms=execution_time,
            metadata={
                'cognitive_style': self.cognitive_style.value,
                'component_count': len(components['controllers']) + len(components['controlled_processes']),
                'hierarchy_levels': components.get('hierarchy_depth', 0)
            }
        )
        
    def _build_control_structure_prompt(self, step1_results: Dict[str, Any]) -> str:
        """Build prompt for control structure identification."""
        base_prompt = self.format_control_structure_prompt(step1_results)
        
        cognitive_prompts = {
            CognitiveStyle.INTUITIVE: """
Focus on natural control relationships and decision-making flows.
Think about WHO makes decisions and WHO carries them out.
Consider both formal and informal control structures.""",
            CognitiveStyle.ANALYTICAL: """
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
"""
        
        return prompt
        
    def _parse_control_structure(self, response: str, step1_results: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response into structured components."""
        try:
            # Clean and parse JSON
            cleaned = clean_json_string(response)
            data = json.loads(cleaned)
            
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
                    
    async def _store_components(self, step2_analysis_id: str, components: Dict[str, Any]) -> None:
        """Store components in database."""
        # Store controllers
        for controller in components['controllers']:
            await self.db_service.execute(
                """
                INSERT INTO system_components 
                (id, analysis_id, identifier, name, component_type, description, 
                 abstraction_level, source, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    step2_analysis_id,
                    controller['identifier'],
                    controller['name'],
                    'controller',
                    controller.get('description', ''),
                    controller.get('abstraction_level', 'service'),
                    controller.get('source', 'inferred'),
                    json.dumps({
                        'authority_level': controller.get('authority_level'),
                        'controls': controller.get('controls', []),
                        'stakeholder_link': controller.get('stakeholder_link'),
                        'trust_level': controller.get('trust_level')
                    })
                )
            )
            
        # Store controlled processes
        for process in components['controlled_processes']:
            await self.db_service.execute(
                """
                INSERT INTO system_components 
                (id, analysis_id, identifier, name, component_type, description, 
                 abstraction_level, source, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    step2_analysis_id,
                    process['identifier'],
                    process['name'],
                    'controlled_process',
                    process.get('description', ''),
                    process.get('abstraction_level', 'service'),
                    'system_description',
                    json.dumps({
                        'criticality': process.get('criticality'),
                        'controlled_by': process.get('controlled_by', [])
                    })
                )
            )
            
        # Store dual-role components
        for dual in components['dual_role_components']:
            await self.db_service.execute(
                """
                INSERT INTO system_components 
                (id, analysis_id, identifier, name, component_type, description, 
                 abstraction_level, source, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    str(uuid.uuid4()),
                    step2_analysis_id,
                    dual['identifier'],
                    dual['name'],
                    'both',
                    dual.get('description', ''),
                    dual.get('abstraction_level', 'service'),
                    'inferred',
                    json.dumps({
                        'controls': dual.get('controls', []),
                        'controlled_by': dual.get('controlled_by', []),
                        'rationale': dual.get('rationale', '')
                    })
                )
            )
            
        # Store hierarchy relationships
        for rel in components['control_hierarchy']:
            # Need to look up component IDs by identifier
            parent_id = await self._get_component_id(step2_analysis_id, rel['parent'])
            child_id = await self._get_component_id(step2_analysis_id, rel['child'])
            
            if parent_id and child_id:
                await self.db_service.execute(
                    """
                    INSERT INTO control_hierarchies 
                    (id, analysis_id, parent_component_id, child_component_id, 
                     relationship_type, description)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        str(uuid.uuid4()),
                        step2_analysis_id,
                        parent_id,
                        child_id,
                        rel.get('relationship_type', 'supervises'),
                        rel.get('description', '')
                    )
                )
                
    async def _get_component_id(self, analysis_id: str, identifier: str) -> Optional[str]:
        """Get component ID by identifier."""
        result = await self.db_service.fetch_one(
            "SELECT id FROM system_components WHERE analysis_id = %s AND identifier = %s",
            (analysis_id, identifier)
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
