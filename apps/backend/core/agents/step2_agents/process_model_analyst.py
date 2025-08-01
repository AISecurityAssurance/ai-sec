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
from core.agents.step1_agents.base_step1 import CognitiveStyle
from core.utils.json_parser import parse_llm_json


class ProcessModelAnalystAgent(BaseStep2Agent):
    """
    Analyzes process models - the controller's view of controlled process state.
    Identifies control algorithm constraints and inadequate control scenarios.
    """
    
    async def analyze(self, step1_analysis_id: str, step2_analysis_id: str, 
                      previous_results: Dict[str, Any]) -> AgentResult:
        """Analyze process models and control algorithm constraints."""
        start_time = datetime.now()
        
        # Get control structure from previous phase
        control_structure = self._extract_control_structure(previous_results)
        control_actions = self._extract_control_actions(previous_results)
        
        # Build prompt
        prompt = self._build_process_model_prompt(control_structure, control_actions)
        
        # Query LLM with retry
        response = await self.query_llm_with_retry(prompt)
        
        # Parse response
        process_models = self._parse_process_models(response)
        
        # Store in database
        await self._store_process_models(step2_analysis_id, process_models)
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return AgentResult(
            agent_type="process_model_analyst",
            success=True,
            data={
                'process_models': process_models['models'],
                'control_algorithms': process_models['algorithms'],
                'inadequate_control_scenarios': process_models['scenarios'],
                'summary': process_models['summary']
            },
            execution_time_ms=execution_time,
            metadata={
                'cognitive_style': self.cognitive_style.value,
                'model_count': len(process_models['models']),
                'scenario_count': len(process_models['scenarios'])
            }
        )
    
    def _build_process_model_prompt(self, control_structure: Dict[str, Any], 
                                    control_actions: List[Dict[str, Any]]) -> str:
        """Build prompt for process model analysis."""
        
        prompt = f"""You are a process model analyst performing STPA-Sec Step 2 analysis.

## Control Structure
Controllers: {json.dumps([c for c in control_structure.get('controllers', [])], indent=2)}
Processes: {json.dumps([p for p in control_structure.get('processes', [])], indent=2)}

## Control Actions
{json.dumps(control_actions, indent=2)}

## Your Task: Analyze Process Models and Control Algorithms

For each controller-process pair, analyze:

1. **Process Model**: The controller's view/belief of the controlled process state
   - What state variables does the controller track?
   - How does the controller update its model?
   - What assumptions does the controller make?
   - Potential mismatches between model and reality

2. **Control Algorithm Constraints**: Rules the controller uses
   - Decision logic for control actions
   - Timing constraints
   - Priority/conflict resolution rules
   - Safety/security constraints

3. **Inadequate Control Scenarios**: Beyond missing/delayed actions
   - Incorrect process model leading to wrong action
   - Conflicting control actions
   - Control action with wrong parameters
   - Action correct but process model update fails
   - Controller receives incorrect feedback

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
    "scenarios": [
        {{
            "identifier": "ICS-1",
            "name": "scenario name",
            "type": "incorrect_model|conflicting_actions|wrong_parameters|failed_update|incorrect_feedback",
            "description": "detailed description",
            "involved_components": ["CTRL-X", "PROC-Y"],
            "preconditions": ["what must be true for this to occur"],
            "consequences": ["potential impacts"],
            "likelihood": "low|medium|high",
            "severity": "low|medium|high|critical"
        }}
    ],
    "summary": "Overall assessment of process model adequacy and control algorithm robustness"
}}

Focus on security-relevant scenarios where attackers could exploit process model weaknesses.
"""
        
        return prompt
    
    def _parse_process_models(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured process models."""
        try:
            data = parse_llm_json(response)
            
            # Validate and enhance
            models = data.get('models', [])
            algorithms = data.get('algorithms', [])
            scenarios = data.get('scenarios', [])
            
            # Add identifiers if missing
            for i, model in enumerate(models):
                if not model.get('identifier'):
                    model['identifier'] = f'PM-{i+1}'
            
            for i, alg in enumerate(algorithms):
                if not alg.get('identifier'):
                    alg['identifier'] = f'ALG-{i+1}'
                    
            for i, scenario in enumerate(scenarios):
                if not scenario.get('identifier'):
                    scenario['identifier'] = f'ICS-{i+1}'
            
            return {
                'models': models,
                'algorithms': algorithms,
                'scenarios': scenarios,
                'summary': data.get('summary', 'Process model analysis completed')
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse process models: {e}")
            # Return minimal structure
            return {
                'models': [],
                'algorithms': [],
                'scenarios': [],
                'summary': f'Process model analysis failed: {str(e)}'
            }
    
    def _extract_control_structure(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract control structure from previous results."""
        control_structure = previous_results.get('control_structure', {})
        
        # Extract from different result formats
        controllers = []
        processes = []
        
        for key, value in control_structure.items():
            if hasattr(value, 'data'):
                components = value.data.get('components', {})
                controllers.extend(components.get('controllers', []))
                processes.extend(components.get('controlled_processes', []))
            elif isinstance(value, dict) and value.get('success'):
                components = value.get('data', {}).get('components', {})
                controllers.extend(components.get('controllers', []))
                processes.extend(components.get('controlled_processes', []))
        
        return {
            'controllers': controllers,
            'processes': processes
        }
    
    def _extract_control_actions(self, previous_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract control actions from previous results."""
        actions = []
        action_results = previous_results.get('control_actions', {})
        
        for key, value in action_results.items():
            if hasattr(value, 'data'):
                actions.extend(value.data.get('control_actions', {}).get('control_actions', []))
            elif isinstance(value, dict) and value.get('success'):
                actions.extend(value.get('data', {}).get('control_actions', {}).get('control_actions', []))
        
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
        
        # Store inadequate control scenarios
        for scenario in process_models['scenarios']:
            await self.db_connection.execute(
                """
                INSERT INTO inadequate_control_scenarios
                (id, analysis_id, identifier, name, scenario_type,
                 description, involved_components, preconditions, 
                 consequences, likelihood, severity)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                ON CONFLICT (identifier, analysis_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    scenario_type = EXCLUDED.scenario_type,
                    description = EXCLUDED.description,
                    involved_components = EXCLUDED.involved_components,
                    preconditions = EXCLUDED.preconditions,
                    consequences = EXCLUDED.consequences,
                    likelihood = EXCLUDED.likelihood,
                    severity = EXCLUDED.severity
                """,
                str(uuid.uuid4()),
                analysis_id,
                scenario['identifier'],
                scenario.get('name'),
                scenario.get('type'),
                scenario.get('description'),
                json.dumps(scenario.get('involved_components', [])),
                json.dumps(scenario.get('preconditions', [])),
                json.dumps(scenario.get('consequences', [])),
                scenario.get('likelihood'),
                scenario.get('severity')
            )