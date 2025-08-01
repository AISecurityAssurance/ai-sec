from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime

from .base_step2 import BaseStep2Agent, AgentResult
from .component_registry import ComponentRegistry
from core.agents.step1_agents.base_step1 import CognitiveStyle
from core.utils.json_parser import parse_llm_json
from .schemas import FEEDBACK_MECHANISM_SCHEMA


class FeedbackMechanismAgent(BaseStep2Agent):
    """
    Identifies feedback mechanisms that inform controllers
    about the state of controlled processes.
    """
    
    async def analyze(self, step1_analysis_id: str, step2_analysis_id: str, **kwargs) -> AgentResult:
        """Identify feedback mechanisms."""
        start_time = datetime.now()
        
        # Get component registry from previous phases
        previous_results = kwargs.get('previous_results', {})
        registry = self._get_registry_from_previous(previous_results)
        
        # Load Step 1 results
        step1_results = await self.load_step1_results(step1_analysis_id)
        
        # Load control structure and actions
        control_structure = await self._load_control_structure(step2_analysis_id)
        control_actions = await self._load_control_actions(step2_analysis_id)
        
        # Build prompt with registry context
        prompt = self._build_feedback_prompt(step1_results, control_structure, control_actions, registry)
        
        # Get LLM response with retry logic
        messages = [
            {"role": "system", "content": "You are an expert systems security analyst who MUST respond with raw JSON only. Do NOT use markdown formatting, code blocks, or backticks. Start your response directly with { and end with }. No ```json tags. You specialize in feedback mechanisms and observability."},
            {"role": "user", "content": prompt}
        ]
        
        # Try structured output first, fall back to regular if needed
        try:
            # Use structured output for guaranteed valid JSON
            structured_response = await self.query_llm_structured(
                messages, 
                FEEDBACK_MECHANISM_SCHEMA,
                temperature=0.3,  # Lower temperature for structured output
                max_tokens=4000
            )
            # Parse response and validate against registry
            feedback_data = self._parse_feedback_mechanisms(structured_response, control_structure, registry)
        except Exception as e:
            self.logger.warning(f"Structured output failed: {e}. Using regular generation.")
            # Fall back to regular generation with retry
            response_text = await self.query_llm_with_retry(messages, temperature=0.7, max_tokens=4000)
            # Parse response
            feedback_data = self._parse_feedback_mechanisms(response_text, control_structure, registry)
        
        # Store in database
        await self._store_feedback_mechanisms(step2_analysis_id, feedback_data)
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AgentResult(
            agent_type="feedback_mechanism",
            success=True,
            data={
                'feedback_mechanisms': feedback_data['feedback_mechanisms'],
                'process_models': feedback_data['process_models'],
                'summary': self._generate_summary(feedback_data),
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
        
        return {
            'components': [dict(c) for c in components],
            'controllers': [dict(c) for c in components if c['component_type'] in ('controller', 'both')],
            'processes': [dict(c) for c in components if c['component_type'] in ('controlled_process', 'both')]
        }
        
    async def _load_control_actions(self, analysis_id: str) -> List[Dict[str, Any]]:
        """Load control actions from database."""
        actions = await self.db_connection.fetch(
            """
            SELECT ca.*, 
                   ctrl.identifier as controller_identifier,
                   proc.identifier as process_identifier
            FROM control_actions ca
            JOIN system_components ctrl ON ca.controller_id = ctrl.id
            JOIN system_components proc ON ca.controlled_process_id = proc.id
            WHERE ca.analysis_id = $1
            """,
            analysis_id
        )
        
        return [dict(a) for a in actions]
    
    def _get_registry_from_previous(self, previous_results: Dict[str, Any]) -> ComponentRegistry:
        """Extract component registry from previous phase results."""
        # Check control actions phase first (most recent)
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
        
    def _build_feedback_prompt(self, step1_results: Dict[str, Any], 
                              control_structure: Dict[str, Any],
                              control_actions: List[Dict[str, Any]],
                              registry: ComponentRegistry) -> str:
        """Build prompt for feedback mechanism identification."""
        base_prompt = self.format_control_structure_prompt(step1_results)
        
        # Get registry context
        registry_context = registry.get_prompt_context()
        
        prompt = f"""{base_prompt}

## Control Structure

{registry_context}

### Controllers from Database:

CRITICAL: Return ONLY valid JSON. Do NOT wrap in markdown code blocks or use backticks.
Start your response with {{ and end with }}.
Ensure all string values properly escape newlines and quotes."""
        for controller in control_structure['controllers']:
            prompt += f"- {controller['identifier']}: {controller['name']}\n"
            
        prompt += "\n### Controlled Processes:\n"
        for process in control_structure['processes']:
            prompt += f"- {process['identifier']}: {process['name']}\n"
            
        prompt += "\n### Control Actions:\n"
        for action in control_actions[:10]:  # Limit to avoid prompt overflow
            prompt += f"- {action['identifier']}: {action['controller_identifier']} → {action['process_identifier']} ({action['action_name']})\n"
            
        cognitive_prompts = {
            CognitiveStyle.TECHNICAL: """
Focus on technical feedback channels and protocols.
Identify specific data flows and measurement points.
Consider latency and reliability requirements.""",
            CognitiveStyle.INTUITIVE: """
Think about information flows that enable control.
Consider implicit feedback through side channels.
Look for missing feedback that should exist.""",
            CognitiveStyle.SYSTEMATIC: """
Map all feedback paths systematically.
Ensure every control action has observable effects.
Identify feedback gaps and blind spots.""",
            CognitiveStyle.CREATIVE: """
Explore non-obvious feedback mechanisms.
Consider emergent information patterns.
Think about adversarial feedback manipulation.""",
            CognitiveStyle.BALANCED: """
Provide comprehensive feedback analysis.
Balance technical detail with conceptual clarity.
Consider both normal and attack scenarios."""
        }
        
        style_prompt = cognitive_prompts.get(self.cognitive_style, cognitive_prompts[CognitiveStyle.BALANCED])
        
        prompt += f"""

## Task: Identify Feedback Mechanisms

{style_prompt}

For each feedback path, identify:

1. **Feedback Mechanisms**: Information flowing back to controllers
   - Unique identifier (FB-X)
   - Source process
   - Target controller
   - Information type and content
   - Timing characteristics
   - Reliability requirements

2. **Process Models**: What controllers believe about system state
   - Which controller maintains the model
   - State variables tracked
   - Update sources and frequency
   - Assumptions and potential mismatches

3. **Feedback Adequacy Analysis**: Assess feedback completeness
   - For each control action:
     * Is there feedback to confirm action execution?
     * Is there feedback to observe action effects?
     * What critical state information is NOT observable?
     * Time delays between action and feedback
   - Identify control actions lacking adequate feedback
   - Note blind spots where controllers lack visibility

Provide your response in the following JSON format:
{{
    "feedback_mechanisms": [
        {{
            "identifier": "FB-1",
            "source_process_id": "PROC-X",
            "target_controller_id": "CTRL-Y",
            "feedback_name": "Feedback Name",
            "information_type": "status/measurement/alert/confirmation",
            "information_content": "What information is conveyed",
            "timing_characteristics": {{
                "frequency": "continuous/periodic/event-driven",
                "latency_requirement": "Timing constraint",
                "staleness_tolerance": "How old can data be"
            }},
            "reliability_requirements": {{
                "availability": "Required uptime",
                "accuracy": "high/medium/low",
                "integrity": "Security requirements"
            }},
            "security_relevance": "Why this feedback matters for security"
        }}
    ],
    "process_models": [
        {{
            "model_name": "Model Name",
            "controller_id": "CTRL-X",
            "state_variables": ["List of tracked variables"],
            "update_sources": ["FB-X", "FB-Y"],
            "update_frequency": "How often model updates",
            "staleness_tolerance": "How out of date can it be",
            "assumptions": ["Key assumptions about state"],
            "potential_mismatches": ["Ways model might diverge from reality"]
        }}
    ],
    "feedback_adequacy": [
        {{
            "control_action_id": "CA-X",
            "has_execution_feedback": true/false,
            "has_effect_feedback": true/false,
            "unobservable_states": ["Critical states not visible to controller"],
            "feedback_delay": "Time between action and feedback",
            "adequacy_assessment": "sufficient/partial/insufficient",
            "adequacy_score": 0.85  # 0-1 scale based on coverage
        }}
    ],
    "feedback_gaps": [
        {{
            "description": "Missing feedback that should exist",
            "impact": "Security impact of this gap",
            "recommendation": "How to address"
        }}
    ],
    "feedback_coverage_metrics": {{
        "overall_coverage_score": 0.75,  # 0-1 scale for entire system
        "critical_gaps_count": 3,  # Number of critical missing feedbacks
        "coverage_by_component": {{
            "CTRL-1": 0.9,  # Individual controller coverage scores
            "CTRL-2": 0.6,
            "PROC-1": 0.8
        }},
        "coverage_by_type": {{
            "execution_feedback": 0.85,
            "effect_feedback": 0.65,
            "state_monitoring": 0.7
        }}
    }},
    "analysis_notes": "Key insights about feedback and observability"
}}

Focus on understanding the complete feedback structure.
Identify all information flows that enable controllers to understand process state.
Consider the completeness and coverage of feedback mechanisms.

CRITICAL: Return ONLY valid JSON. Do NOT wrap in markdown code blocks or use backticks.
Start your response with {{ and end with }}.
Ensure all string values properly escape newlines and quotes."""
        
        return prompt
        
    def _parse_feedback_mechanisms(self, response: Any, control_structure: Dict[str, Any], registry: ComponentRegistry) -> Dict[str, Any]:
        """Parse LLM response into feedback mechanisms."""
        try:
            # Handle both string and dict responses (dict from structured output)
            if isinstance(response, dict):
                data = response
            else:
                data = parse_llm_json(response)
            
            # Build lookup maps
            component_map = {c['identifier']: c['id'] for c in control_structure['components']}
            
            # Process feedback mechanisms
            mechanisms = []
            validation_errors = []
            
            for feedback in data.get('feedback_mechanisms', []):
                source_id_str = feedback.get('source_process_id')
                target_id_str = feedback.get('target_controller_id')
                
                # Validate against registry
                if not registry.validate_component_reference(source_id_str):
                    validation_errors.append(f"Invalid source process reference: {source_id_str}")
                    continue
                    
                if not registry.validate_component_reference(target_id_str):
                    validation_errors.append(f"Invalid target controller reference: {target_id_str}")
                    continue
                
                source_id = component_map.get(source_id_str)
                target_id = component_map.get(target_id_str)
                
                if source_id and target_id:
                    feedback['source_db_id'] = source_id
                    feedback['target_db_id'] = target_id
                    mechanisms.append(feedback)
                    
                    # Register the feedback reference in the registry
                    registry.add_reference(source_id_str, target_id_str)
                    
            # Process process models
            models = []
            for model in data.get('process_models', []):
                controller_id_str = model.get('controller_id')
                
                # Validate against registry
                if not registry.validate_component_reference(controller_id_str):
                    validation_errors.append(f"Invalid controller reference in process model: {controller_id_str}")
                    continue
                    
                controller_id = component_map.get(controller_id_str)
                if controller_id:
                    model['controller_db_id'] = controller_id
                    models.append(model)
            
            # Add validation errors to analysis notes
            analysis_notes = data.get('analysis_notes', '')
            if validation_errors:
                analysis_notes += f"\n\nValidation errors:\n" + "\n".join(validation_errors)
                    
            return {
                'feedback_mechanisms': mechanisms,
                'process_models': models,
                'feedback_gaps': data.get('feedback_gaps', []),
                'analysis_notes': analysis_notes,
                'validation_errors': validation_errors
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse feedback mechanisms: {e}")
            return {
                'feedback_mechanisms': [],
                'process_models': [],
                'feedback_gaps': [],
                'analysis_notes': f'Parse error: {str(e)}',
                'validation_errors': []
            }
            
    async def _store_feedback_mechanisms(self, analysis_id: str, feedback_data: Dict[str, Any]) -> None:
        """Store feedback mechanisms in database."""
        # Store feedback mechanisms
        for feedback in feedback_data['feedback_mechanisms']:
            await self.db_connection.execute(
                """
                INSERT INTO feedback_mechanisms
                (id, analysis_id, identifier, source_process_id, target_controller_id,
                 feedback_name, information_type, information_content,
                 timing_characteristics, reliability_requirements)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                """,
                str(uuid.uuid4()),
                analysis_id,
                feedback['identifier'],
                feedback['source_db_id'],
                feedback['target_db_id'],
                feedback['feedback_name'],
                feedback['information_type'],
                feedback.get('information_content', ''),
                json.dumps(feedback.get('timing_characteristics', {})),
                json.dumps(feedback.get('reliability_requirements', {}))
            )
            
        # Store process models
        for model in feedback_data['process_models']:
            await self.db_connection.execute(
                """
                INSERT INTO process_models
                (id, controller_id, model_name, state_variables, update_sources,
                 update_frequency, staleness_tolerance, assumptions)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                """,
                str(uuid.uuid4()),
                model['controller_db_id'],
                model['model_name'],
                json.dumps(model.get('state_variables', [])),
                model.get('update_sources', []),
                model.get('update_frequency', 'unknown'),
                model.get('staleness_tolerance', 'unknown'),
                json.dumps(model.get('assumptions', []))
            )
            
    def _generate_summary(self, feedback_data: Dict[str, Any]) -> str:
        """Generate summary of feedback mechanisms."""
        mechanism_count = len(feedback_data['feedback_mechanisms'])
        model_count = len(feedback_data['process_models'])
        gap_count = len(feedback_data.get('feedback_gaps', []))
        
        summary = f"Identified {mechanism_count} feedback mechanisms and {model_count} process models"
        
        if gap_count > 0:
            summary += f", with {gap_count} critical feedback gaps"
            
        # Summarize by type
        type_counts = {}
        for feedback in feedback_data['feedback_mechanisms']:
            info_type = feedback.get('information_type', 'unknown')
            type_counts[info_type] = type_counts.get(info_type, 0) + 1
            
        if type_counts:
            type_summary = ", ".join([f"{count} {type}" for type, count in type_counts.items()])
            summary += f"\n\nFeedback types: {type_summary}"
            
        if feedback_data.get('analysis_notes'):
            summary += f"\n\n{feedback_data['analysis_notes']}"
            
        return summary