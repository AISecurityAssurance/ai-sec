from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime

from .base_step2 import BaseStep2Agent, AgentResult
from .component_registry import ComponentRegistry
from core.agents.step1_agents.base_step1 import CognitiveStyle
from core.utils.json_parser import parse_llm_json
from .schemas import CONTROL_ACTION_SCHEMA


class ControlActionMappingAgent(BaseStep2Agent):
    """
    Maps control actions from controllers to controlled processes.
    Identifies what commands flow through the system.
    """
    
    async def analyze(self, step1_analysis_id: str, step2_analysis_id: str, **kwargs) -> AgentResult:
        """Map control actions between components."""
        start_time = datetime.now()
        
        # Get component registry from previous phase
        previous_results = kwargs.get('previous_results', {})
        registry = None
        if 'control_structure' in previous_results:
            control_phase = previous_results['control_structure']
            if isinstance(control_phase, dict):
                for agent_key, agent_result in control_phase.items():
                    if hasattr(agent_result, 'data') and 'component_registry' in agent_result.data:
                        registry = agent_result.data['component_registry']
                    elif isinstance(agent_result, dict) and 'data' in agent_result and 'component_registry' in agent_result['data']:
                        registry = agent_result['data']['component_registry']
        
        if registry is None:
            registry = ComponentRegistry()
        
        # Load Step 1 results
        step1_results = await self.load_step1_results(step1_analysis_id)
        
        # Load control structure from previous phase
        control_structure = await self._load_control_structure(step2_analysis_id)
        
        # Build prompt with component registry context
        prompt = self._build_control_action_prompt(step1_results, control_structure, registry)
        
        # Get LLM response with retry logic
        messages = [
            {"role": "system", "content": "You are an expert systems security analyst who MUST respond with raw JSON only. Do NOT use markdown formatting, code blocks, or backticks. Start your response directly with { and end with }. No ```json tags. You specialize in control action identification and mapping."},
            {"role": "user", "content": prompt}
        ]
        
        # Try structured output first, fall back to regular if needed
        try:
            # Use structured output for guaranteed valid JSON
            structured_response = await self.query_llm_structured(
                messages, 
                CONTROL_ACTION_SCHEMA,
                temperature=0.3,  # Lower temperature for structured output
                max_tokens=4000
            )
            # Parse response and validate against registry
            control_actions = self._parse_control_actions(structured_response, control_structure, registry)
        except Exception as e:
            self.logger.warning(f"Structured output failed: {e}. Using regular generation.")
            # Fall back to regular generation with retry
            response_text = await self.query_llm_with_retry(messages, temperature=0.7, max_tokens=4000)
            # Parse response and validate against registry
            control_actions = self._parse_control_actions(response_text, control_structure, registry)
        
        # Store in database
        await self._store_control_actions(step2_analysis_id, control_actions)
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AgentResult(
            agent_type="control_action_mapping",
            success=True,
            data={
                'control_actions': control_actions,
                'summary': self._generate_summary(control_actions),
                'component_registry': registry
            },
            execution_time_ms=execution_time,
            metadata={'cognitive_style': self.cognitive_style.value}
        )
        
    async def _load_control_structure(self, analysis_id: str) -> Dict[str, Any]:
        """Load control structure components from database."""
        # Load controllers
        controllers = await self.db_connection.fetch(
            """
            SELECT id, identifier, name, metadata
            FROM system_components
            WHERE analysis_id = $1 AND component_type IN ('controller', 'both')
            """,
            analysis_id
        )
        
        # Load controlled processes
        processes = await self.db_connection.fetch(
            """
            SELECT id, identifier, name, metadata
            FROM system_components
            WHERE analysis_id = $1 AND component_type IN ('controlled_process', 'both')
            """,
            analysis_id
        )
        
        return {
            'controllers': [dict(c) for c in controllers],
            'processes': [dict(p) for p in processes]
        }
        
    def _build_control_action_prompt(self, step1_results: Dict[str, Any], control_structure: Dict[str, Any], registry: ComponentRegistry) -> str:
        """Build prompt for control action mapping."""
        base_prompt = self.format_control_structure_prompt(step1_results)
        
        # Get component context from registry
        registry_context = registry.get_prompt_context()
        
        prompt = f"""{base_prompt}

## Identified Control Structure

{registry_context}

### Controllers from Database:

CRITICAL: Return ONLY valid JSON. Do NOT wrap in markdown code blocks or use backticks.
Start your response with {{ and end with }}.
Ensure all string values properly escape newlines and quotes."""
        for controller in control_structure['controllers']:
            prompt += f"- {controller['identifier']}: {controller['name']}\n"
            
        prompt += "\n### Controlled Processes from Database:\n"
        for process in control_structure['processes']:
            prompt += f"- {process['identifier']}: {process['name']}\n"
            
        cognitive_prompts = {
            CognitiveStyle.SYSTEMATIC: """
Focus on systematic mapping of all control relationships.
Ensure every controller has defined actions.
Map both direct and indirect control paths.""",
            CognitiveStyle.TECHNICAL: """
Focus on technical control protocols and implementations.
Identify specific command types and parameters.
Consider timing and sequencing requirements.""",
            CognitiveStyle.INTUITIVE: """
Think about natural control flows and decision patterns.
Consider implicit control actions not explicitly stated.
Look for emergent control behaviors.""",
            CognitiveStyle.CREATIVE: """
Explore non-obvious control mechanisms.
Consider multi-path control actions.
Identify potential control conflicts or races.""",
            CognitiveStyle.BALANCED: """
Provide comprehensive control action mapping.
Balance completeness with clarity.
Consider both normal and exceptional cases."""
        }
        
        style_prompt = cognitive_prompts.get(self.cognitive_style, cognitive_prompts[CognitiveStyle.BALANCED])
        
        prompt += f"""

## Task: Map Control Actions

{style_prompt}

For each control relationship, identify:

1. **Control Actions**: Specific commands or controls
   - Unique identifier (CA-X)
   - Controller source
   - Controlled process target
   - Action name and description
   - Action type (command/configuration/permission/monitoring)
   - Authority level (mandatory/optional/emergency)
   - Timing requirements

2. **Control Contexts**: When actions are valid
   - Required system states
   - Prohibited states
   - Preconditions
   - Expected outcomes

3. **Control Action Completeness**: Ensure comprehensive coverage
   - Every controller must have at least one outgoing control action
   - Every controlled process must receive at least one control action
   - Identify any "orphan" components without control relationships
   - Note any controllers that only receive but don't send control

Provide your response in the following JSON format:
{{
    "control_actions": [
        {{
            "identifier": "CA-1",
            "controller_id": "CTRL-X",
            "controlled_process_id": "PROC-Y",
            "action_name": "Action Name",
            "action_description": "What this action does",
            "action_type": "command/configuration/permission/monitoring",
            "authority_level": "mandatory/optional/emergency",
            "timing_requirements": {{
                "type": "periodic/on-demand/event-driven",
                "details": "Timing details"
            }},
            "security_relevance": "Why this matters for security"
        }}
    ],
    "control_contexts": [
        {{
            "control_action_id": "CA-X",
            "valid_states": ["List of states where action is valid"],
            "prohibited_states": ["List of states where action is NOT allowed"],
            "preconditions": ["What must be true before action"],
            "postconditions": ["What should be true after action"]
        }}
    ],
    "completeness_check": {{
        "controllers_without_actions": ["List of controller IDs with no outgoing actions"],
        "processes_without_control": ["List of process IDs with no incoming control"],
        "orphan_components": ["Components with no control relationships"],
        "coverage_assessment": "Summary of completeness"
    }},
    "analysis_notes": "Key insights about control actions"
}}

Focus on security-critical control actions.
Consider both intended and potential misuse cases.

CRITICAL: Return ONLY valid JSON. Do NOT wrap in markdown code blocks or use backticks.
Start your response with {{ and end with }}.
Ensure all string values properly escape newlines and quotes."""
        
        return prompt
        
    def _parse_control_actions(self, response: Any, control_structure: Dict[str, Any], registry: ComponentRegistry) -> Dict[str, Any]:
        """Parse LLM response into control actions."""
        try:
            # Handle both string and dict responses (dict from structured output)
            if isinstance(response, dict):
                data = response
            else:
                data = parse_llm_json(response)
            
            # Build lookup maps
            controller_map = {c['identifier']: c['id'] for c in control_structure['controllers']}
            process_map = {p['identifier']: p['id'] for p in control_structure['processes']}
            
            # Process control actions
            actions = []
            validation_errors = []
            
            for action in data.get('control_actions', []):
                controller_id_str = action.get('controller_id')
                process_id_str = action.get('controlled_process_id')
                
                # Validate against registry
                if not registry.validate_component_reference(controller_id_str):
                    validation_errors.append(f"Invalid controller reference: {controller_id_str}")
                    continue
                    
                if not registry.validate_component_reference(process_id_str):
                    validation_errors.append(f"Invalid process reference: {process_id_str}")
                    continue
                
                # Map identifiers to database IDs
                controller_id = controller_map.get(controller_id_str)
                process_id = process_map.get(process_id_str)
                
                if controller_id and process_id:
                    action['controller_db_id'] = controller_id
                    action['process_db_id'] = process_id
                    actions.append(action)
                    
                    # Register the control action reference in the registry
                    registry.add_reference(controller_id_str, process_id_str)
                    
            # Store contexts with actions
            context_map = {}
            for context in data.get('control_contexts', []):
                action_id = context.get('control_action_id')
                if action_id:
                    context_map[action_id] = context
                    
            # Add validation errors to analysis notes
            analysis_notes = data.get('analysis_notes', '')
            if validation_errors:
                analysis_notes += f"\n\nValidation errors:\n" + "\n".join(validation_errors)
                    
            return {
                'control_actions': actions,
                'control_contexts': context_map,
                'analysis_notes': analysis_notes,
                'validation_errors': validation_errors
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse control actions: {e}")
            return {
                'control_actions': [],
                'control_contexts': {},
                'analysis_notes': f'Parse error: {str(e)}',
                'validation_errors': []
            }
            
    async def _store_control_actions(self, analysis_id: str, actions_data: Dict[str, Any]) -> None:
        """Store control actions in database."""
        for action in actions_data['control_actions']:
            action_id = str(uuid.uuid4())
            
            # Store control action
            await self.db_connection.execute(
                """
                INSERT INTO control_actions
                (id, analysis_id, identifier, controller_id, controlled_process_id,
                 action_name, action_description, action_type, timing_requirements, authority_level)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                action_id,
                analysis_id,
                action['identifier'],
                action['controller_db_id'],
                action['process_db_id'],
                action['action_name'],
                action.get('action_description', ''),
                action.get('action_type', 'command'),
                json.dumps(action.get('timing_requirements', {})),
                action.get('authority_level', 'optional')
            )
            
            # Store context if available
            context = actions_data['control_contexts'].get(action['identifier'])
            if context:
                await self.db_connection.execute(
                    """
                    INSERT INTO control_action_contexts
                    (id, control_action_id, required_system_state, prohibited_states,
                     preconditions, postconditions)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    str(uuid.uuid4()),
                    action_id,
                    ', '.join(context.get('valid_states', [])),
                    context.get('prohibited_states', []),
                    json.dumps(context.get('preconditions', [])),
                    json.dumps(context.get('postconditions', []))
                )
                
    def _generate_summary(self, actions_data: Dict[str, Any]) -> str:
        """Generate summary of control actions."""
        action_count = len(actions_data['control_actions'])
        
        # Count by type
        type_counts = {}
        for action in actions_data['control_actions']:
            action_type = action.get('action_type', 'unknown')
            type_counts[action_type] = type_counts.get(action_type, 0) + 1
            
        summary = f"Identified {action_count} control actions"
        
        if type_counts:
            type_summary = ", ".join([f"{count} {type}" for type, count in type_counts.items()])
            summary += f" ({type_summary})"
            
        if actions_data.get('analysis_notes'):
            summary += f"\n\n{actions_data['analysis_notes']}"
            
        return summary