"""
Process Model Analysis Agent for Step 2 STPA-Sec

Analyzes the controller's view of controlled process state and identifies
control algorithm constraints.
"""
from typing import Dict, Any, List, Optional
import json
import uuid
from datetime import datetime
from .base_step2 import BaseStep2Agent, AgentResult
from .component_registry import ComponentRegistry
from core.agents.step1_agents.base_step1 import CognitiveStyle
from core.utils.json_parser import parse_llm_json
from .schemas import PROCESS_MODEL_SCHEMA


class ProcessModelAnalystAgent(BaseStep2Agent):
    """
    Analyzes process models - the controller's view of controlled process state.
    Identifies control algorithm constraints and inadequate control scenarios.
    """
    
    async def analyze(self, step1_analysis_id: str, step2_analysis_id: str, 
                      previous_results: Dict[str, Any]) -> AgentResult:
        """Analyze process models and control algorithm constraints."""
        start_time = datetime.now()
        
        try:
            # Get component registry from previous phases
            registry = self._get_registry_from_previous(previous_results)
            
            # Get control structure from previous phase
            control_structure = self._extract_control_structure(previous_results)
            control_actions = self._extract_control_actions(previous_results)
            
            # Build prompt with registry context
            prompt = self._build_process_model_prompt(control_structure, control_actions, registry)
            
            # Prepare messages for LLM
            messages = [
                {"role": "system", "content": "You are a process model analyst performing STPA-Sec Step 2 analysis. Respond with valid JSON only, no markdown formatting."},
                {"role": "user", "content": prompt}
            ]
            
            # Try structured output first, fall back to regular if needed
            try:
                # Use structured output for guaranteed valid JSON
                structured_response = await self.query_llm_structured(
                    messages, 
                    PROCESS_MODEL_SCHEMA,
                    temperature=0.3,  # Lower temperature for structured output
                    max_tokens=4000
                )
                # Parse response and validate against registry
                process_models = self._parse_process_models(structured_response, registry)
            except Exception as e:
                self.logger.warning(f"Structured output failed: {e}. Using regular generation.")
                # Fall back to regular generation with retry
                response = await self.query_llm_with_retry(messages)
                # Parse response and validate against registry
                process_models = self._parse_process_models(response, registry)
            
            # Store in database
            await self._store_process_models(step2_analysis_id, process_models)
            
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            return AgentResult(
                agent_type="process_model_analyst",
                success=True,
                data={
                    'process_models': process_models.get('models', []),
                    'control_algorithms': process_models.get('algorithms', []),
                    'insights': process_models.get('insights', {}),
                    'summary': process_models.get('summary', 'Process model analysis completed'),
                    'component_registry': registry
                },
                execution_time_ms=execution_time,
                metadata={
                    'cognitive_style': self.cognitive_style.value,
                    'model_count': len(process_models.get('models', [])),
                    'algorithm_count': len(process_models.get('algorithms', []))
                }
            )
        except Exception as e:
            self.logger.error(f"Process model analysis failed: {str(e)}")
            return AgentResult(
                agent_type="process_model_analyst",
                success=False,
                data={'error': str(e)},
                execution_time_ms=int((datetime.now() - start_time).total_seconds() * 1000)
            )
    
    def _get_registry_from_previous(self, previous_results: Dict[str, Any]) -> ComponentRegistry:
        """Extract component registry from previous phase results."""
        # Check different phases in reverse order (most recent first)
        phases_to_check = ['control_context', 'feedback_trust', 'control_actions', 'control_structure']
        
        for phase_name in phases_to_check:
            if phase_name in previous_results:
                phase_data = previous_results[phase_name]
                if isinstance(phase_data, dict):
                    for agent_key, agent_result in phase_data.items():
                        if hasattr(agent_result, 'data') and 'component_registry' in agent_result.data:
                            return agent_result.data['component_registry']
                        elif isinstance(agent_result, dict) and 'data' in agent_result and 'component_registry' in agent_result['data']:
                            return agent_result['data']['component_registry']
        
        # If no registry found, create new one
        return ComponentRegistry()
    
    def _build_process_model_prompt(self, control_structure: Dict[str, Any], 
                                    control_actions: List[Dict[str, Any]], 
                                    registry: ComponentRegistry) -> str:
        """Build prompt for process model analysis."""
        
        # Get registry context
        registry_context = registry.get_prompt_context()
        
        prompt = f"""You are a process model analyst performing STPA-Sec Step 2 analysis.

## Control Structure

{registry_context}

### Controllers from Previous Analysis:
{json.dumps([c for c in control_structure.get('controllers', [])], indent=2)}

### Processes from Previous Analysis:
{json.dumps([p for p in control_structure.get('processes', [])], indent=2)}

## Control Actions
{json.dumps(control_actions, indent=2)}

## Your Task: Analyze Process Models and Control Algorithms

This is Step 2 analysis - focus on understanding HOW control works, not identifying unsafe conditions.

For each controller-process pair, analyze:

1. **Process Model**: The controller's internal representation of process state
   - What state variables does the controller track?
   - How does the controller update its model?
   - What information sources feed the model?
   - Update frequency and data freshness requirements

2. **Control Algorithm**: The logic and rules the controller uses
   - Decision logic for control actions
   - Input processing and evaluation
   - Priority/conflict resolution between actions
   - Timing and sequencing constraints
   - Operational constraints and limits

Provide response as JSON:
{{
    "models": [
        {{
            "identifier": "PM-1",
            "controller_id": "CTRL-X",
            "process_id": "PROC-Y",
            "state_variables": [
                {{
                    "name": "variable_name",
                    "type": "boolean|numeric|enum|composite",
                    "description": "what this represents",
                    "update_mechanism": "how it's updated",
                    "potential_issues": ["list of potential mismatches"]
                }}
            ],
            "assumptions": ["list of assumptions the controller makes"],
            "update_frequency": "continuous|periodic|event-driven",
            "staleness_risk": "low|medium|high"
        }}
    ],
    "algorithms": [
        {{
            "identifier": "ALG-1",
            "controller_id": "CTRL-X",
            "name": "algorithm name",
            "description": "what it does",
            "constraints": [
                {{
                    "type": "timing|safety|security|resource",
                    "constraint": "specific constraint",
                    "enforcement": "how it's enforced",
                    "violation_impact": "what happens if violated"
                }}
            ],
            "decision_logic": "description of decision process",
            "conflict_resolution": "how conflicts are handled"
        }}
    ],
    "insights": {{
        "model_coverage": "How well process models represent actual system state",
        "algorithm_sophistication": "Level of control algorithm complexity",
        "information_dependencies": "Critical information flows for control decisions",
        "timing_characteristics": "Which algorithms have strict timing requirements",
        "coordination_needs": "How controllers coordinate their actions"
    }},
    "summary": "Overall description of process modeling and control algorithm approach"
}}

Remember: This is Step 2 - focus on understanding HOW control works, not on identifying problems or unsafe scenarios.
"""
        
        return prompt
    
    def _parse_process_models(self, response: Any, registry: ComponentRegistry) -> Dict[str, Any]:
        """Parse LLM response into structured process models."""
        try:
            # Handle both string and dict responses (dict from structured output)
            if isinstance(response, dict):
                data = response
            else:
                data = parse_llm_json(response)
            
            # Validate and enhance
            models = data.get('models', [])
            algorithms = data.get('algorithms', [])
            insights = data.get('insights', {})
            validation_errors = []
            
            # Validate and add identifiers if missing
            validated_models = []
            for i, model in enumerate(models):
                if not model.get('identifier'):
                    model['identifier'] = f'PM-{i+1}'
                    
                # Validate component references
                controller_id = model.get('controller_id')
                process_id = model.get('process_id')
                
                if controller_id and not registry.validate_component_reference(controller_id):
                    validation_errors.append(f"Invalid controller reference in process model: {controller_id}")
                    continue
                    
                if process_id and not registry.validate_component_reference(process_id):
                    validation_errors.append(f"Invalid process reference in process model: {process_id}")
                    continue
                    
                validated_models.append(model)
            
            validated_algorithms = []
            for i, alg in enumerate(algorithms):
                if not alg.get('identifier'):
                    alg['identifier'] = f'ALG-{i+1}'
                    
                # Validate controller reference
                controller_id = alg.get('controller_id')
                if controller_id and not registry.validate_component_reference(controller_id):
                    validation_errors.append(f"Invalid controller reference in algorithm: {controller_id}")
                    continue
                    
                validated_algorithms.append(alg)
            
            # Add validation errors to summary if any
            summary = data.get('summary', 'Process model analysis completed')
            if validation_errors:
                summary += f"\n\nValidation errors:\n" + "\n".join(validation_errors)
            
            return {
                'models': validated_models,
                'algorithms': validated_algorithms,
                'insights': insights,
                'summary': summary,
                'validation_errors': validation_errors
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse process models: {e}")
            # Return minimal structure
            return {
                'models': [],
                'algorithms': [],
                'insights': {},
                'summary': f'Process model analysis failed: {str(e)}',
                'validation_errors': []
            }
    
    def _extract_control_structure(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract control structure from previous results."""
        controllers = []
        processes = []
        
        # Check different possible locations for control structure data
        # First check if there's a control_structure phase result
        if 'control_structure' in previous_results:
            control_phase = previous_results['control_structure']
            
            # Handle phase results which contain agent results
            if isinstance(control_phase, dict):
                for agent_key, agent_result in control_phase.items():
                    if hasattr(agent_result, 'data'):
                        components = agent_result.data.get('components', {})
                        controllers.extend(components.get('controllers', []))
                        processes.extend(components.get('controlled_processes', []))
                    elif isinstance(agent_result, dict) and agent_result.get('success'):
                        components = agent_result.get('data', {}).get('components', {})
                        controllers.extend(components.get('controllers', []))
                        processes.extend(components.get('controlled_processes', []))
        
        # Also check if data is directly in previous_results
        if 'components' in previous_results:
            components = previous_results['components']
            controllers.extend(components.get('controllers', []))
            processes.extend(components.get('controlled_processes', []))
        
        return {
            'controllers': controllers,
            'processes': processes
        }
    
    def _extract_control_actions(self, previous_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract control actions from previous results."""
        actions = []
        
        # Check if there's a control_actions phase result
        if 'control_actions' in previous_results:
            action_phase = previous_results['control_actions']
            
            # Handle phase results which contain agent results
            if isinstance(action_phase, dict):
                for agent_key, agent_result in action_phase.items():
                    if hasattr(agent_result, 'data'):
                        control_actions_data = agent_result.data.get('control_actions', [])
                        if isinstance(control_actions_data, dict):
                            actions.extend(control_actions_data.get('control_actions', []))
                        elif isinstance(control_actions_data, list):
                            actions.extend(control_actions_data)
                    elif isinstance(agent_result, dict) and agent_result.get('success'):
                        data = agent_result.get('data', {})
                        control_actions_data = data.get('control_actions', [])
                        if isinstance(control_actions_data, dict):
                            actions.extend(control_actions_data.get('control_actions', []))
                        elif isinstance(control_actions_data, list):
                            actions.extend(control_actions_data)
        
        # Also check if control_actions is directly in previous_results
        if 'control_actions' in previous_results and isinstance(previous_results['control_actions'], list):
            actions.extend(previous_results['control_actions'])
        
        return actions
    
    async def _store_process_models(self, analysis_id: str, process_models: Dict[str, Any]) -> None:
        """Store process models in database."""
        # Store each process model
        for model in process_models['models']:
            await self.db_connection.execute(
                """
                INSERT INTO process_models 
                (id, analysis_id, identifier, controller_id, process_id, 
                 state_variables, assumptions, update_frequency, staleness_risk)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (identifier, analysis_id) DO UPDATE SET
                    state_variables = EXCLUDED.state_variables,
                    assumptions = EXCLUDED.assumptions,
                    update_frequency = EXCLUDED.update_frequency,
                    staleness_risk = EXCLUDED.staleness_risk
                """,
                str(uuid.uuid4()),
                analysis_id,
                model['identifier'],
                model.get('controller_id'),
                model.get('process_id'),
                json.dumps(model.get('state_variables', [])),
                json.dumps(model.get('assumptions', [])),
                model.get('update_frequency'),
                model.get('staleness_risk')
            )
        
        # Store control algorithms
        for alg in process_models['algorithms']:
            await self.db_connection.execute(
                """
                INSERT INTO control_algorithms
                (id, analysis_id, identifier, controller_id, name, 
                 description, constraints, decision_logic, conflict_resolution)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                ON CONFLICT (identifier, analysis_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    constraints = EXCLUDED.constraints,
                    decision_logic = EXCLUDED.decision_logic,
                    conflict_resolution = EXCLUDED.conflict_resolution
                """,
                str(uuid.uuid4()),
                analysis_id,
                alg['identifier'],
                alg.get('controller_id'),
                alg.get('name'),
                alg.get('description'),
                json.dumps(alg.get('constraints', [])),
                alg.get('decision_logic'),
                alg.get('conflict_resolution')
            )
        
        # Store insights as metadata
        await self.db_connection.execute(
            """
            UPDATE step2_analyses 
            SET metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object('process_model_insights', $1)
            WHERE id = $2
            """,
            json.dumps(process_models.get('insights', {})),
            analysis_id
        )