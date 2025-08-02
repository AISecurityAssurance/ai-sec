from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime

from .base_step2 import BaseStep2Agent, AgentResult
from .component_registry import ComponentRegistry
from core.agents.step1_agents.base_step1 import CognitiveStyle
from core.utils.json_parser import parse_llm_json
from .schemas import TRUST_BOUNDARY_SCHEMA


class TrustBoundaryAgent(BaseStep2Agent):
    """
    Identifies trust boundaries between system components
    and analyzes security implications.
    """
    
    async def analyze(self, step1_analysis_id: str, step2_analysis_id: str, **kwargs) -> AgentResult:
        """Identify trust boundaries."""
        start_time = datetime.now()
        
        # Get component registry from previous phases
        previous_results = kwargs.get('previous_results', {})
        registry = self._get_registry_from_previous(previous_results)
        
        # Load Step 1 results
        step1_results = await self.load_step1_results(step1_analysis_id)
        
        # Load control structure and actions
        control_structure = await self._load_control_structure(step2_analysis_id)
        control_actions = await self._load_control_actions(step2_analysis_id)
        feedback_mechanisms = await self._load_feedback_mechanisms(step2_analysis_id)
        
        # Build prompt with registry context
        prompt = self._build_trust_boundary_prompt(step1_results, control_structure, 
                                                  control_actions, feedback_mechanisms, registry)
        
        # Get LLM response with retry logic
        messages = [
            {"role": "system", "content": "You are an expert systems security analyst specializing in trust boundaries and security perimeters. You MUST respond with raw JSON only. Do NOT use markdown formatting, code blocks, or backticks. Start your response directly with { and end with }. No ```json tags."},
            {"role": "user", "content": prompt}
        ]
        
        # Try structured output first, fall back to regular if needed
        try:
            # Use structured output for guaranteed valid JSON
            structured_response = await self.query_llm_structured(
                messages, 
                TRUST_BOUNDARY_SCHEMA,
                temperature=0.3,  # Lower temperature for structured output
                max_tokens=4000
            )
            # Parse response and validate against registry
            trust_data = self._parse_trust_boundaries(structured_response, control_structure, registry)
        except Exception as e:
            self.logger.warning(f"Structured output failed: {e}. Using regular generation.")
            # Fall back to regular generation with retry
            response_text = await self.query_llm_with_retry(messages, temperature=0.7, max_tokens=4000)
            # Parse response and validate against registry
            trust_data = self._parse_trust_boundaries(response_text, control_structure, registry)
        
        # Store in database
        await self._store_trust_boundaries(step2_analysis_id, trust_data)
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AgentResult(
            agent_type="trust_boundary",
            success=True,
            data={
                'trust_boundaries': trust_data['trust_boundaries'],
                'security_implications': trust_data['security_implications'],
                'summary': self._generate_summary(trust_data),
                'component_registry': registry
            },
            execution_time_ms=execution_time,
            metadata={'cognitive_style': self.cognitive_style.value}
        )
        
    async def _load_control_structure(self, analysis_id: str) -> Dict[str, Any]:
        """Load control structure components from database."""
        components = await self.db_connection.fetch(
            """
            SELECT id, identifier, name, component_type, metadata
            FROM system_components
            WHERE analysis_id = $1
            """,
            analysis_id
        )
        
        return {'components': [dict(c) for c in components]}
        
    async def _load_control_actions(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Load control actions from database."""
        actions = await self.db_connection.fetch(
            """
            SELECT ca.*, 
                   ctrl.identifier as controller_identifier,
                   ctrl.name as controller_name,
                   proc.identifier as process_identifier,
                   proc.name as process_name
            FROM control_actions ca
            JOIN system_components ctrl ON ca.controller_id = ctrl.id
            JOIN system_components proc ON ca.controlled_process_id = proc.id
            WHERE ca.analysis_id = $1
            """,
            analysis_id
        )
        
        return [dict(a) for a in actions]
        
    async def _load_feedback_mechanisms(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Load feedback mechanisms from database."""
        feedbacks = await self.db_connection.fetch(
            """
            SELECT fb.*, 
                   src.identifier as source_identifier,
                   src.name as source_name,
                   tgt.identifier as target_identifier,
                   tgt.name as target_name
            FROM feedback_mechanisms fb
            JOIN system_components src ON fb.source_process_id = src.id
            JOIN system_components tgt ON fb.target_controller_id = tgt.id
            WHERE fb.analysis_id = $1
            """,
            analysis_id
        )
        
        return [dict(f) for f in feedbacks]
    
    def _get_registry_from_previous(self, previous_results: Dict[str, Any]) -> ComponentRegistry:
        """Extract component registry from previous phase results."""
        # Check feedback mechanisms phase (most recent)
        if 'feedback_mechanisms' in previous_results:
            feedback_phase = previous_results['feedback_mechanisms']
            if isinstance(feedback_phase, dict):
                for agent_key, agent_result in feedback_phase.items():
                    if hasattr(agent_result, 'data') and 'component_registry' in agent_result.data:
                        return agent_result.data['component_registry']
                    elif isinstance(agent_result, dict) and 'data' in agent_result and 'component_registry' in agent_result['data']:
                        return agent_result['data']['component_registry']
        
        # Check control actions phase
        if 'control_actions' in previous_results:
            action_phase = previous_results['control_actions']
            if isinstance(action_phase, dict):
                for agent_key, agent_result in action_phase.items():
                    if hasattr(agent_result, 'data') and 'component_registry' in agent_result.data:
                        return agent_result.data['component_registry']
                    elif isinstance(agent_result, dict) and 'data' in agent_result and 'component_registry' in agent_result['data']:
                        return agent_result['data']['component_registry']
        
        # Fall back to control structure phase
        if 'control_structure' in previous_results:
            control_phase = previous_results['control_structure']
            if isinstance(control_phase, dict):
                for agent_key, agent_result in control_phase.items():
                    if hasattr(agent_result, 'data') and 'component_registry' in agent_result.data:
                        return agent_result.data['component_registry']
                    elif isinstance(agent_result, dict) and 'data' in agent_result and 'component_registry' in agent_result['data']:
                        return agent_result['data']['component_registry']
        
        # If no registry found, create new one
        return ComponentRegistry()
        
    def _build_trust_boundary_prompt(self, step1_results: Dict[str, Any], 
                                    control_structure: Dict[str, Any],
                                    control_actions: List[Dict[str, Any]],
                                    feedback_mechanisms: List[Dict[str, Any]],
                                    registry: ComponentRegistry) -> str:
        """Build prompt for trust boundary identification."""
        base_prompt = self.format_control_structure_prompt(step1_results)
        
        # Get registry context
        registry_context = registry.get_prompt_context()
        
        prompt = f"""{base_prompt}

## Control Structure Components

{registry_context}

### Components from Database:

CRITICAL: Return ONLY valid JSON. Do NOT wrap in markdown code blocks or use backticks.
Start your response with {{ and end with }}.
Ensure all string values properly escape newlines and quotes."""
        for component in control_structure['components']:
            prompt += f"- {component['identifier']}: {component['name']} ({component['component_type']})\n"
            
        prompt += "\n## Control Flows\n### Control Actions:\n"
        for action in control_actions[:10]:
            prompt += f"- {action['controller_name']} → {action['process_name']}: {action['action_name']}\n"
            
        prompt += "\n### Feedback Mechanisms:\n"
        for feedback in feedback_mechanisms[:10]:
            prompt += f"- {feedback['source_name']} → {feedback['target_name']}: {feedback['feedback_name']}\n"
            
        # Include stakeholder trust levels from Step 1
        prompt += "\n## Stakeholder Trust Levels:\n"
        for stakeholder in step1_results['stakeholders']:
            if stakeholder.get('trust_level'):
                prompt += f"- {stakeholder['name']}: {stakeholder['trust_level']} trust\n"
                
        cognitive_prompts = {
            CognitiveStyle.SYSTEMATIC: """
Systematically analyze all component interactions.
Map trust relationships based on data flows.
Ensure complete coverage of all boundaries.""",
            CognitiveStyle.CREATIVE: """
Think creatively about trust assumptions.
Consider non-obvious trust relationships.
Explore potential trust violations.""",
            CognitiveStyle.TECHNICAL: """
Focus on technical trust mechanisms.
Identify authentication and authorization points.
Consider cryptographic boundaries.""",
            CognitiveStyle.INTUITIVE: """
Think about natural trust boundaries.
Consider organizational and human factors.
Look for implicit trust assumptions.""",
            CognitiveStyle.BALANCED: """
Provide comprehensive trust boundary analysis.
Balance technical and organizational factors.
Consider both design and implementation."""
        }
        
        style_prompt = cognitive_prompts.get(self.cognitive_style, cognitive_prompts[CognitiveStyle.BALANCED])
        
        prompt += f"""

## Task: Identify Trust Boundaries (Step 2 - Descriptive Focus)

{style_prompt}

Remember: This is Step 2 - describe existing trust mechanisms, not analyze vulnerabilities.

For each trust boundary, identify:

1. **Trust Boundaries**: Security perimeters between components
   - Unique identifier (TB-X)
   - Components on each side
   - Type of boundary
   - Trust relationship direction
   - Existing security mechanisms

2. **Trust Mechanisms**: How trust is currently implemented
   - Authentication protocols in use
   - Authorization schemes deployed
   - Data protection mechanisms active
   - Trust assumptions built into the design
   - Verification methods employed

Provide your response in the following JSON format:
{{
    "trust_boundaries": [
        {{
            "identifier": "TB-1",
            "boundary_name": "Boundary Name",
            "boundary_type": "network/authentication/authorization/data_classification",
            "component_a_id": "Component identifier on side A",
            "component_b_id": "Component identifier on side B",
            "trust_direction": "bidirectional/a_trusts_b/b_trusts_a/none",
            "trust_rationale": "Why this trust relationship exists",
            "authentication_method": "How components authenticate",
            "authorization_method": "How access is controlled",
            "data_protection": {{
                "encryption": "Required encryption level",
                "integrity": "Integrity protection needs",
                "confidentiality": "Confidentiality requirements"
            }},
            "security_controls": ["List of existing security controls at boundary"],
            "trust_assumptions": ["Assumptions about trust built into the design"],
            "verification_methods": ["How trust is verified or validated"]
        }}
    ],
    "trust_mechanisms": {{
        "authentication_protocols": ["List of authentication methods in use"],
        "authorization_schemes": ["How access control is implemented"],
        "data_protection": ["Encryption, integrity checks, etc."],
        "trust_establishment": ["How trust relationships are established"],
        "trust_maintenance": ["How trust is maintained over time"]
    }},
    "analysis_notes": "Key insights about trust boundaries"
}}

Focus on describing existing trust mechanisms.
Document how trust is currently implemented in the system.
Save vulnerability analysis for Step 3.

CRITICAL: Return ONLY valid JSON. Do NOT wrap in markdown code blocks or use backticks.
Start your response with {{ and end with }}.
Ensure all string values properly escape newlines and quotes."""
        
        return prompt
        
    def _parse_trust_boundaries(self, response: Any, control_structure: Dict[str, Any], registry: ComponentRegistry) -> Dict[str, Any]:
        """Parse LLM response into trust boundaries."""
        try:
            # Handle both string and dict responses (dict from structured output)
            if isinstance(response, dict):
                data = response
            else:
                data = parse_llm_json(response)
            
            # Build lookup map
            component_map = {c['identifier']: c['id'] for c in control_structure['components']}
            
            # Process trust boundaries
            boundaries = []
            validation_errors = []
            
            for boundary in data.get('trust_boundaries', []):
                comp_a_id_str = boundary.get('component_a_id')
                comp_b_id_str = boundary.get('component_b_id')
                
                # Validate against registry
                if not registry.validate_component_reference(comp_a_id_str):
                    validation_errors.append(f"Invalid component A reference: {comp_a_id_str}")
                    continue
                    
                if not registry.validate_component_reference(comp_b_id_str):
                    validation_errors.append(f"Invalid component B reference: {comp_b_id_str}")
                    continue
                
                comp_a_id = component_map.get(comp_a_id_str)
                comp_b_id = component_map.get(comp_b_id_str)
                
                if comp_a_id and comp_b_id:
                    boundary['component_a_db_id'] = comp_a_id
                    boundary['component_b_db_id'] = comp_b_id
                    boundaries.append(boundary)
                    
                    # Register the trust boundary reference in the registry
                    registry.add_reference(comp_a_id_str, comp_b_id_str)
                    
            # Add validation errors to analysis notes
            analysis_notes = data.get('analysis_notes', '')
            if validation_errors:
                analysis_notes += f"\n\nValidation errors:\n" + "\n".join(validation_errors)
                    
            return {
                'trust_boundaries': boundaries,
                'security_implications': data.get('security_implications', []),
                'trust_violations': data.get('trust_violations', []),
                'analysis_notes': analysis_notes,
                'validation_errors': validation_errors
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse trust boundaries: {e}")
            return {
                'trust_boundaries': [],
                'security_implications': [],
                'trust_violations': [],
                'analysis_notes': f'Parse error: {str(e)}',
                'validation_errors': []
            }
            
    async def _store_trust_boundaries(self, analysis_id: str, trust_data: Dict[str, Any]) -> None:
        """Store trust boundaries in database."""
        for boundary in trust_data['trust_boundaries']:
            await self.db_connection.execute(
                """
                INSERT INTO trust_boundaries
                (id, analysis_id, identifier, boundary_name, boundary_type,
                 component_a_id, component_b_id, trust_direction,
                 authentication_method, authorization_method, data_protection_requirements)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                """,
                str(uuid.uuid4()),
                analysis_id,
                boundary['identifier'],
                boundary['boundary_name'],
                boundary.get('boundary_type', 'network'),
                boundary['component_a_db_id'],
                boundary['component_b_db_id'],
                boundary.get('trust_direction', 'none'),
                boundary.get('authentication_method', ''),
                boundary.get('authorization_method', ''),
                json.dumps(boundary.get('data_protection', {}))
            )
            
    def _generate_summary(self, trust_data: Dict[str, Any]) -> str:
        """Generate summary of trust boundaries."""
        boundary_count = len(trust_data['trust_boundaries'])
        violation_count = len(trust_data.get('trust_violations', []))
        
        summary = f"Identified {boundary_count} trust boundaries"
        
        # Count by type
        type_counts = {}
        for boundary in trust_data['trust_boundaries']:
            boundary_type = boundary.get('boundary_type', 'unknown')
            type_counts[boundary_type] = type_counts.get(boundary_type, 0) + 1
            
        if type_counts:
            type_summary = ", ".join([f"{count} {type}" for type, count in type_counts.items()])
            summary += f" ({type_summary})"
            
        if violation_count > 0:
            summary += f"\n\nIdentified {violation_count} potential trust violations"
            
        # Count trust directions
        direction_counts = {}
        for boundary in trust_data['trust_boundaries']:
            direction = boundary.get('trust_direction', 'unknown')
            direction_counts[direction] = direction_counts.get(direction, 0) + 1
            
        if direction_counts:
            dir_summary = ", ".join([f"{count} {dir}" for dir, count in direction_counts.items()])
            summary += f"\n\nTrust relationships: {dir_summary}"
            
        if trust_data.get('analysis_notes'):
            summary += f"\n\n{trust_data['analysis_notes']}"
            
        return summary