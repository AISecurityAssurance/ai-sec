"""Control Context Analyst for STPA-Sec Step 2.

This agent describes the execution mechanics of control actions - their
triggers, decision logic, and operational modes. It focuses on documenting
HOW the control system works, not determining when actions are valid/invalid
(which is Step 3 analysis).
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging
from uuid import uuid4

from core.utils.json_parser import parse_llm_json
from .base_step2 import BaseStep2Agent, CognitiveStyle, AgentResult


class ControlContextAnalystAgent(BaseStep2Agent):
    """Analyzes control contexts without identifying unsafe states."""
    
    def __init__(self, model_provider, db_connection: Any, cognitive_style: CognitiveStyle = CognitiveStyle.BALANCED):
        super().__init__(model_provider, db_connection, cognitive_style)
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def get_agent_type(self) -> str:
        return "control_context_analyst"
    
    async def analyze(self, step1_analysis_id: str, step2_analysis_id: str, 
                     previous_results: Dict[str, Any]) -> AgentResult:
        """Analyze control contexts for identified control actions."""
        # Store analysis IDs for use in methods
        self.step1_analysis_id = step1_analysis_id
        self.step2_analysis_id = step2_analysis_id
        
        try:
            # Get control structure and control actions
            control_structure = await self._get_control_structure()
            control_actions = await self._get_control_actions()
            
            if not control_actions:
                return AgentResult(
                    agent_type=self.get_agent_type(),
                    success=False,
                    data={'error': "No control actions found to analyze contexts for"},
                    execution_time_ms=0
                )
            
            # Build prompt
            prompt = self._build_prompt(control_structure, control_actions)
            
            # Query LLM with retry logic
            messages = [{"role": "user", "content": prompt}]
            response = await self.query_llm_with_retry(messages)
            
            # Parse response
            control_contexts = self._parse_control_contexts(response, control_actions)
            
            # Save to database
            await self._save_control_contexts(control_contexts)
            
            # Generate summary
            summary = self._generate_summary(control_contexts)
            
            return AgentResult(
                agent_type=self.get_agent_type(),
                success=True,
                data={
                    'control_contexts': control_contexts['control_contexts'],
                    'operational_modes': control_contexts['operational_modes'],
                    'mode_transitions': control_contexts['mode_transitions'],
                    'summary': summary
                },
                execution_time_ms=0,
                metadata={
                    'cognitive_style': self.cognitive_style.value,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Control context analysis failed: {str(e)}")
            return AgentResult(
                agent_type=self.get_agent_type(),
                success=False,
                data={'error': str(e)},
                execution_time_ms=0
            )
    
    def _build_prompt(self, control_structure: Dict[str, Any], control_actions: List[Dict[str, Any]]) -> str:
        """Build prompt for control context analysis."""
        prompt = f"""You are a control systems expert analyzing WHEN and UNDER WHAT CONDITIONS control actions occur.

## Important: Focus on Control Mechanics (Step 2)
You are performing Step 2 analysis - describing how the control system works.
DO NOT analyze validity, safety, or identify unsafe conditions - that's Step 3.
Focus on documenting:
- WHAT triggers control actions (inputs, events, conditions)
- HOW controllers make decisions (logic, algorithms)
- WHAT operational modes exist
- HOW the system transitions between modes

## System Description
{control_structure.get('description', 'Control structure identified')}

## Control Actions to Analyze
"""
        
        # List control actions
        for action in control_actions[:20]:  # Limit to avoid prompt overflow
            prompt += f"\n### {action['identifier']}: {action['action_name']}"
            prompt += f"\n- From: {action['controller_identifier']}"
            prompt += f"\n- To: {action['process_identifier']}"
            
            if action.get('description'):
                prompt += f"\n- Purpose: {action['description']}"
                
        cognitive_prompts = {
            CognitiveStyle.SYSTEMATIC: """
Systematically analyze all control contexts.
Map conditions and triggers for each action.
Ensure completeness of context coverage.""",
            CognitiveStyle.CREATIVE: """
Think about edge cases and special conditions.
Consider implicit contexts and assumptions.
Explore non-obvious triggering conditions.""",
            CognitiveStyle.TECHNICAL: """
Focus on technical triggering conditions.
Analyze timing and sequencing requirements.
Consider implementation-specific contexts.""",
            CognitiveStyle.INTUITIVE: """
Think about operational contexts.
Consider human factors in control decisions.
Look for implicit contextual assumptions.""",
            CognitiveStyle.BALANCED: """
Provide comprehensive context analysis.
Balance technical detail with clarity.
Consider all types of contextual factors."""
        }
        
        style_prompt = cognitive_prompts.get(self.cognitive_style, cognitive_prompts[CognitiveStyle.BALANCED])
        
        prompt += f"""

## Task: Analyze Control Contexts

{style_prompt}

For each control action, describe:

1. **Execution Mechanics**: How the action is triggered and executed
   - Triggering events or conditions
   - Input signals processed
   - Environmental factors considered
   - Execution frequency/timing

2. **Operational Modes**: System operating states
   - Mode definitions and purposes
   - Available control actions per mode
   - Mode transition triggers
   - Mode-specific behaviors

3. **Decision Process**: The controller's decision-making process
   - Information sources used
   - Processing algorithms or rules
   - Priority schemes
   - Conflict resolution mechanisms

Provide your response in the following JSON format:
{{
    "control_contexts": [
        {{
            "control_action_id": "CA-X",
            "execution_context": {{
                "triggers": ["List of triggering conditions"],
                "preconditions": ["Required conditions before execution"],
                "environmental_factors": ["External factors considered"],
                "timing_requirements": {{
                    "frequency": "How often action can/should occur",
                    "response_time": "Required response time",
                    "duration": "How long action takes"
                }}
            }},
            "decision_logic": {{
                "inputs_evaluated": ["What information is considered"],
                "decision_criteria": "How decision is made",
                "priority": "high/medium/low",
                "conflict_resolution": "How conflicts with other actions are resolved"
            }},
            "applicable_modes": ["Mode names where this action is available"]
        }}
    ],
    "operational_modes": [
        {{
            "mode_name": "Mode name",
            "description": "What this mode represents",
            "entry_conditions": ["How system enters this mode"],
            "exit_conditions": ["How system exits this mode"],
            "active_controllers": ["Controllers active in this mode"],
            "available_actions": ["Actions available in this mode"],
            "mode_constraints": ["Constraints while in this mode"]
        }}
    ],
    "mode_transitions": [
        {{
            "from_mode": "Starting mode",
            "to_mode": "Target mode",
            "transition_trigger": "What causes transition",
            "transition_actions": ["Actions taken during transition"],
            "transition_time": "Expected transition duration"
        }}
    ],
    "analysis_notes": "Key insights about control contexts and operational modes"
}}

Remember: This is Step 2 - describe HOW the system works, not WHEN actions are safe/unsafe.

CRITICAL: Return ONLY valid JSON. Do NOT wrap in markdown code blocks or use backticks.
Start your response with {{ and end with }}.
"""
        
        return prompt
    
    def _parse_control_contexts(self, response: str, control_actions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse LLM response into control contexts."""
        try:
            data = parse_llm_json(response)
            
            # Build action lookup map - ensure each action is a dict
            action_map = {}
            for a in control_actions:
                if isinstance(a, dict) and 'identifier' in a and 'id' in a:
                    action_map[a['identifier']] = a['id']
            
            # Process control contexts
            contexts = data.get('control_contexts', [])
            if isinstance(contexts, list):
                for context in contexts:
                    if isinstance(context, dict):
                        action_id = context.get('control_action_id')
                        if action_id and action_id in action_map:
                            context['control_action_uuid'] = action_map[action_id]
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to parse control contexts: {e}")
            return {
                'control_contexts': [],
                'operational_modes': [],
                'mode_transitions': [],
                'parse_error': str(e)
            }
    
    async def _save_control_contexts(self, control_contexts: Dict[str, Any]):
        """Save control contexts to database."""
        if not self.db_connection:
            return
            
        # Save control contexts
        for context in control_contexts.get('control_contexts', []):
            await self.db_connection.execute("""
                INSERT INTO control_contexts 
                (id, analysis_id, control_action_id, execution_context, 
                 decision_logic, valid_modes, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (analysis_id, control_action_id) 
                DO UPDATE SET 
                    execution_context = $4,
                    decision_logic = $5,
                    valid_modes = $6
            """,
                str(uuid4()),
                self.step2_analysis_id,
                context.get('control_action_uuid'),
                json.dumps(context.get('execution_context', {})),
                json.dumps(context.get('decision_logic', {})),
                context.get('applicable_modes', []),
                datetime.now()
            )
        
        # Save operational modes
        for mode in control_contexts.get('operational_modes', []):
            await self.db_connection.execute("""
                INSERT INTO operational_modes
                (id, analysis_id, mode_name, description, entry_conditions,
                 exit_conditions, active_controllers, available_actions,
                 mode_constraints, created_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
                str(uuid4()),
                self.step2_analysis_id,
                mode['mode_name'],
                mode['description'],
                mode.get('entry_conditions', []),
                mode.get('exit_conditions', []),
                mode.get('active_controllers', []),
                mode.get('available_actions', []),
                mode.get('mode_constraints', []),
                datetime.now()
            )
    
    def _generate_summary(self, control_contexts: Dict[str, Any]) -> str:
        """Generate summary of control context analysis."""
        contexts = control_contexts.get('control_contexts', [])
        modes = control_contexts.get('operational_modes', [])
        transitions = control_contexts.get('mode_transitions', [])
        
        summary = f"Analyzed {len(contexts)} control action contexts"
        
        if modes:
            summary += f"\nIdentified {len(modes)} operational modes"
            
        if transitions:
            summary += f"\nMapped {len(transitions)} mode transitions"
            
        # Analyze timing requirements - ensure c is a dict
        time_critical = 0
        for c in contexts:
            if isinstance(c, dict):
                exec_ctx = c.get('execution_context', {})
                if isinstance(exec_ctx, dict):
                    timing = exec_ctx.get('timing_requirements', {})
                    if isinstance(timing, dict) and timing.get('response_time'):
                        time_critical += 1
        
        if time_critical:
            summary += f"\n{time_critical} actions have critical timing requirements"
            
        # Analyze decision complexity - ensure c is a dict
        complex_decisions = 0
        for c in contexts:
            if isinstance(c, dict):
                decision = c.get('decision_logic', {})
                if isinstance(decision, dict):
                    inputs = decision.get('inputs_evaluated', [])
                    if isinstance(inputs, list) and len(inputs) > 3:
                        complex_decisions += 1
        
        if complex_decisions:
            summary += f"\n{complex_decisions} actions have complex decision logic"
            
        return summary
        
    async def _get_control_structure(self) -> Dict[str, Any]:
        """Get control structure from database."""
        result = await self.db_connection.fetchrow("""
            SELECT description, components, hierarchy
            FROM control_structures
            WHERE analysis_id = $1
        """, self.step2_analysis_id)
        
        if result:
            return {
                'description': result['description'],
                'components': json.loads(result['components']) if result['components'] else [],
                'hierarchy': json.loads(result['hierarchy']) if result['hierarchy'] else {}
            }
        return {}
    
    async def _get_control_actions(self) -> List[Dict[str, Any]]:
        """Get control actions from database."""
        results = await self.db_connection.fetch("""
            SELECT ca.id, ca.identifier, ca.action_name, ca.action_description as description,
                   ctrl.identifier as controller_identifier,
                   proc.identifier as process_identifier
            FROM control_actions ca
            LEFT JOIN system_components ctrl ON ca.controller_id = ctrl.id
            LEFT JOIN system_components proc ON ca.controlled_process_id = proc.id
            WHERE ca.analysis_id = $1
            ORDER BY ca.identifier
        """, self.step2_analysis_id)
        
        return [dict(row) for row in results]