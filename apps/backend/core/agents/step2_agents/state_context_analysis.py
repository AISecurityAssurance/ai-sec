"""
State Context Analysis Agent for Step 2 STPA-Sec
Analyzes when control actions are valid/invalid based on system state.
"""
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime

from .base_step2 import BaseStep2Agent, AgentResult
from core.agents.step1_agents.base_step1 import CognitiveStyle
from core.utils.json_parser import parse_llm_json


class StateContextAnalysisAgent(BaseStep2Agent):
    """
    Analyzes state-dependent validity of control actions.
    Identifies when actions should/shouldn't be performed.
    """
    
    async def analyze(self, step1_analysis_id: str, step2_analysis_id: str, **kwargs) -> AgentResult:
        """Analyze state contexts for control actions."""
        start_time = datetime.now()
        
        # Load Step 1 results
        step1_results = await self.load_step1_results(step1_analysis_id)
        
        # Load control actions and existing contexts
        control_actions = await self._load_control_actions(step2_analysis_id)
        
        # Build prompt
        prompt = self._build_state_context_prompt(step1_results, control_actions)
        
        # Get LLM response
        messages = [
            {"role": "system", "content": "You are an expert systems security analyst specializing in state-dependent control analysis."},
            {"role": "user", "content": prompt}
        ]
        
        response = await self.model_provider.generate(messages, temperature=0.7, max_tokens=4000)
        
        # Parse response
        state_data = self._parse_state_contexts(response.content, control_actions)
        
        # Store in database
        await self._store_state_contexts(step2_analysis_id, state_data)
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AgentResult(
            agent_type="state_context_analysis",
            success=True,
            data={
                'state_contexts': state_data['enhanced_contexts'],
                'operational_modes': state_data['operational_modes'],
                'summary': self._generate_summary(state_data)
            },
            execution_time_ms=execution_time,
            metadata={'cognitive_style': self.cognitive_style.value}
        )
        
    async def _load_control_actions(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Load control actions with their contexts."""
        actions = await self.db_connection.fetch(
            """
            SELECT ca.*, 
                   ctrl.identifier as controller_identifier,
                   ctrl.name as controller_name,
                   proc.identifier as process_identifier,
                   proc.name as process_name,
                   cac.required_system_state,
                   cac.prohibited_states,
                   cac.preconditions,
                   cac.postconditions
            FROM control_actions ca
            JOIN system_components ctrl ON ca.controller_id = ctrl.id
            JOIN system_components proc ON ca.controlled_process_id = proc.id
            LEFT JOIN control_action_contexts cac ON ca.id = cac.control_action_id
            WHERE ca.analysis_id = $1
            """,
            analysis_id
        )
        
        return [dict(a) for a in actions]
        
    def _build_state_context_prompt(self, step1_results: Dict[str, Any], 
                                   control_actions: List[Dict[str, Any]]) -> str:
        """Build prompt for state context analysis."""
        base_prompt = self.format_control_structure_prompt(step1_results)
        
        prompt = f"""{base_prompt}

## Control Actions to Analyze
"""
        for action in control_actions:
            prompt += f"\n### {action['identifier']}: {action['action_name']}\n"
            prompt += f"- From: {action['controller_name']}\n"
            prompt += f"- To: {action['process_name']}\n"
            prompt += f"- Type: {action.get('action_type', 'unknown')}\n"
            prompt += f"- Authority: {action.get('authority_level', 'unknown')}\n"
            
            if action.get('required_system_state'):
                prompt += f"- Current context: {action['required_system_state']}\n"
                
        cognitive_prompts = {
            CognitiveStyle.SYSTEMATIC: """
Systematically analyze all possible system states.
Map complete state space for each control action.
Ensure no critical states are missed.""",
            CognitiveStyle.CREATIVE: """
Think creatively about edge cases and corner states.
Consider unusual state combinations.
Explore non-obvious state dependencies.""",
            CognitiveStyle.TECHNICAL: """
Focus on technical state representations.
Consider implementation-specific states.
Analyze timing and sequencing constraints.""",
            CognitiveStyle.INTUITIVE: """
Think about natural operational states.
Consider human factors in state transitions.
Look for implicit state assumptions.""",
            CognitiveStyle.BALANCED: """
Provide comprehensive state analysis.
Balance completeness with clarity.
Consider both normal and exceptional states."""
        }
        
        style_prompt = cognitive_prompts.get(self.cognitive_style, cognitive_prompts[CognitiveStyle.BALANCED])
        
        prompt += f"""

## Task: Analyze State Contexts

{style_prompt}

For each control action, provide:

1. **Enhanced State Contexts**: When actions are valid/invalid
   - Required states for safe operation
   - Prohibited states where action is dangerous
   - Timing constraints
   - State transition requirements

2. **Operational Modes**: System-wide states affecting control
   - Mode definitions
   - Entry/exit conditions
   - Valid actions per mode
   - Mode transition safety

Provide your response in the following JSON format:
{{
    "enhanced_contexts": [
        {{
            "control_action_id": "{action['identifier']}",
            "safe_states": [
                {{
                    "state_name": "State description",
                    "conditions": ["List of conditions that must be true"],
                    "rationale": "Why action is safe in this state"
                }}
            ],
            "unsafe_states": [
                {{
                    "state_name": "State description",
                    "conditions": ["List of conditions"],
                    "hazard": "What hazard could occur",
                    "severity": "critical/high/medium/low"
                }}
            ],
            "timing_constraints": {{
                "too_early": "Hazard if provided too early",
                "too_late": "Hazard if provided too late",
                "wrong_duration": "Hazard if wrong duration",
                "wrong_sequence": "Hazard if out of sequence"
            }},
            "required_transitions": [
                {{
                    "from_state": "Starting state",
                    "to_state": "Target state",
                    "conditions": ["Transition requirements"]
                }}
            ]
        }}
    ],
    "operational_modes": [
        {{
            "mode_name": "Mode name",
            "description": "What this mode represents",
            "entry_conditions": ["How to enter this mode"],
            "exit_conditions": ["How to leave this mode"],
            "valid_control_actions": ["{action['identifier']}", ...],
            "restricted_actions": ["Actions not allowed"],
            "security_implications": "Security impact of this mode"
        }}
    ],
    "state_conflicts": [
        {{
            "description": "Conflicting state requirements",
            "affected_actions": ["CA-X", "CA-Y"],
            "resolution": "How to resolve conflict"
        }}
    ],
    "analysis_notes": "Key insights about state-dependent control"
}}

Focus on security-critical state dependencies.
Identify states where control could be compromised.
Consider attacker manipulation of system state.
"""
        
        return prompt
        
    def _parse_state_contexts(self, response: str, control_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse LLM response into state contexts."""
        try:
            data = parse_llm_json(response, self.logger)
            
            # Build action lookup map
            action_map = {a['identifier']: a['id'] for a in control_actions}
            
            # Process enhanced contexts
            enhanced_contexts = []
            for context in data.get('enhanced_contexts', []):
                action_id = action_map.get(context.get('control_action_id'))
                if action_id:
                    context['control_action_db_id'] = action_id
                    enhanced_contexts.append(context)
                    
            return {
                'enhanced_contexts': enhanced_contexts,
                'operational_modes': data.get('operational_modes', []),
                'state_conflicts': data.get('state_conflicts', []),
                'analysis_notes': data.get('analysis_notes', '')
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse state contexts: {e}")
            return {
                'enhanced_contexts': [],
                'operational_modes': [],
                'state_conflicts': [],
                'analysis_notes': f'Parse error: {str(e)}'
            }
            
    async def _store_state_contexts(self, analysis_id: str, state_data: Dict[str, Any]) -> None:
        """Store state contexts in database."""
        # Update control action contexts with enhanced analysis
        for context in state_data['enhanced_contexts']:
            action_id = context['control_action_db_id']
            
            # Build state lists
            safe_states = [s['state_name'] for s in context.get('safe_states', [])]
            unsafe_states = [s['state_name'] for s in context.get('unsafe_states', [])]
            
            # Check if context already exists
            existing = await self.db_connection.fetchrow(
                "SELECT id FROM control_action_contexts WHERE control_action_id = $1",
                action_id
            )
            
            if existing:
                # Update existing context
                await self.db_connection.execute(
                    """
                    UPDATE control_action_contexts
                    SET required_system_state = $2,
                        prohibited_states = $3,
                        preconditions = $4,
                        postconditions = $5
                    WHERE id = $1
                    """,
                    existing['id'],
                    ', '.join(safe_states),
                    unsafe_states,
                    json.dumps(context.get('timing_constraints', {})),
                    json.dumps(context.get('required_transitions', []))
                )
            else:
                # Create new context
                await self.db_connection.execute(
                    """
                    INSERT INTO control_action_contexts
                    (id, control_action_id, required_system_state, prohibited_states,
                     preconditions, postconditions)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    str(uuid.uuid4()),
                    action_id,
                    ', '.join(safe_states),
                    unsafe_states,
                    json.dumps(context.get('timing_constraints', {})),
                    json.dumps(context.get('required_transitions', []))
                )
                
        # Store operational modes
        for mode in state_data['operational_modes']:
            await self.db_connection.execute(
                """
                INSERT INTO operational_modes
                (id, analysis_id, mode_name, description, entry_conditions,
                 exit_conditions, available_control_actions, restricted_actions)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                str(uuid.uuid4()),
                analysis_id,
                mode['mode_name'],
                mode.get('description', ''),
                json.dumps(mode.get('entry_conditions', [])),
                json.dumps(mode.get('exit_conditions', [])),
                mode.get('valid_control_actions', []),
                mode.get('restricted_actions', [])
            )
            
    def _generate_summary(self, state_data: Dict[str, Any]) -> str:
        """Generate summary of state context analysis."""
        context_count = len(state_data['enhanced_contexts'])
        mode_count = len(state_data['operational_modes'])
        conflict_count = len(state_data.get('state_conflicts', []))
        
        summary = f"Analyzed state contexts for {context_count} control actions"
        
        if mode_count > 0:
            summary += f"\nIdentified {mode_count} operational modes"
            
        # Count unsafe states
        unsafe_count = 0
        critical_count = 0
        for context in state_data['enhanced_contexts']:
            unsafe_states = context.get('unsafe_states', [])
            unsafe_count += len(unsafe_states)
            critical_count += len([s for s in unsafe_states if s.get('severity') == 'critical'])
            
        if unsafe_count > 0:
            summary += f"\n\nFound {unsafe_count} unsafe state conditions"
            if critical_count > 0:
                summary += f" ({critical_count} critical)"
                
        if conflict_count > 0:
            summary += f"\n\nIdentified {conflict_count} state conflicts requiring resolution"
            
        if state_data.get('analysis_notes'):
            summary += f"\n\n{state_data['analysis_notes']}"
            
        return summary