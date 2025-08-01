"""
Step 2 Coordinator for STPA-Sec Control Structure Analysis
"""
from typing import Dict, Any, List, Optional
import uuid
import json
from datetime import datetime
import asyncio
from pathlib import Path

from core.agents.step1_agents.base_step1 import CognitiveStyle
from .base_step2 import AgentResult
import asyncpg
import logging
from core.validation import Step2Validator

from .control_structure_analyst import ControlStructureAnalystAgent
from .control_action_mapping import ControlActionMappingAgent
from .state_context_analysis import StateContextAnalysisAgent
from .feedback_mechanism import FeedbackMechanismAgent
from .trust_boundary import TrustBoundaryAgent
from .synthesis_enhancement import Step2SynthesisEnhancer
from .process_model_analyst import ProcessModelAnalystAgent


class Step2Coordinator:
    """
    Coordinates Step 2 STPA-Sec analysis agents.
    Focuses on control structure identification and analysis.
    """
    
    def __init__(self, model_provider, db_connection: asyncpg.Connection, output_dir: Optional[Path] = None):
        self.model_provider = model_provider
        self.db_connection = db_connection
        self.logger = logging.getLogger(self.__class__.__name__)
        self.output_dir = output_dir
        self.validator = Step2Validator()
        self.synthesis_enhancer = Step2SynthesisEnhancer()
        
        # Define execution phases for Step 2
        self.phases = [
            {
                'name': 'control_structure',
                'agents': ['control_structure_analyst'],
                'description': 'Identify controllers and controlled processes'
            },
            {
                'name': 'control_actions', 
                'agents': ['control_action_mapping'],
                'description': 'Map control actions between components'
            },
            {
                'name': 'state_context',
                'agents': ['state_context_analysis'],
                'description': 'Analyze state-dependent control contexts'
            },
            {
                'name': 'feedback_trust',
                'agents': ['feedback_mechanism', 'trust_boundary'],
                'description': 'Identify feedback loops and trust boundaries',
                'parallel': True
            },
            {
                'name': 'process_models',
                'agents': ['process_model_analyst'],
                'description': 'Analyze process models and control algorithms'
            }
        ]
        
        # Agent configuration
        self.agent_config = {
            'standard': {
                'control_structure_analyst': [CognitiveStyle.BALANCED],
                'control_action_mapping': [CognitiveStyle.SYSTEMATIC],
                'state_context_analysis': [CognitiveStyle.SYSTEMATIC],
                'feedback_mechanism': [CognitiveStyle.TECHNICAL],
                'trust_boundary': [CognitiveStyle.SYSTEMATIC],
                'process_model_analyst': [CognitiveStyle.SYSTEMATIC]
            },
            'enhanced': {
                'control_structure_analyst': [CognitiveStyle.INTUITIVE, CognitiveStyle.SYSTEMATIC],
                'control_action_mapping': [CognitiveStyle.TECHNICAL, CognitiveStyle.SYSTEMATIC],
                'state_context_analysis': [CognitiveStyle.SYSTEMATIC, CognitiveStyle.CREATIVE],
                'feedback_mechanism': [CognitiveStyle.TECHNICAL, CognitiveStyle.INTUITIVE],
                'trust_boundary': [CognitiveStyle.SYSTEMATIC, CognitiveStyle.CREATIVE],
                'process_model_analyst': [CognitiveStyle.SYSTEMATIC, CognitiveStyle.TECHNICAL]
            }
        }
        
    async def coordinate(self, step1_analysis_id: str, execution_mode: str = 'standard', **kwargs) -> Dict[str, Any]:
        """
        Coordinate Step 2 analysis.
        """
        start_time = datetime.now()
        
        # Ensure Step 2 tables have correct schema
        try:
            # Check if system_components table exists and has identifier column
            table_exists = await self.db_connection.fetchval(
                "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'system_components')"
            )
            if table_exists:
                columns = await self.db_connection.fetch(
                    "SELECT column_name FROM information_schema.columns WHERE table_name = 'system_components'"
                )
                self.logger.info(f"system_components columns: {[c['column_name'] for c in columns]}")
                
                # Try to query identifier column
                await self.db_connection.fetchval("SELECT identifier FROM system_components LIMIT 1")
        except Exception as e:
            if "column" in str(e) and "identifier" in str(e):
                self.logger.error(f"Step 2 schema error: {e}")
                self.logger.warning("Step 2 tables have incorrect schema. Please run migrations.")
        
        # Create Step 2 analysis record
        step2_analysis_id = await self._create_step2_analysis(step1_analysis_id, execution_mode)
        
        # Execute phases
        phase_results = {}
        for phase in self.phases:
            self.logger.info(f"Executing Step 2 phase: {phase['name']}")
            
            if phase.get('parallel', False):
                # Run agents in parallel
                results = await self._execute_parallel_agents(
                    phase['agents'], 
                    step2_analysis_id,
                    step1_analysis_id,
                    execution_mode,
                    phase_results
                )
            else:
                # Run agents sequentially
                results = await self._execute_sequential_agents(
                    phase['agents'],
                    step2_analysis_id, 
                    step1_analysis_id,
                    execution_mode,
                    phase_results
                )
                
            phase_results[phase['name']] = results
            
            # Validate phase results
            validation = self._validate_phase(phase['name'], results)
            if not validation['valid']:
                self.logger.warning(f"Phase {phase['name']} validation issues: {validation['errors']}")
                
        # Final synthesis
        synthesis = await self._synthesize_results(step2_analysis_id, phase_results)
        
        # Store final results
        await self._store_final_results(step2_analysis_id, synthesis)
        
        execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Prepare results
        results = {
            'analysis_id': step2_analysis_id,
            'step1_analysis_id': step1_analysis_id,
            'execution_mode': execution_mode,
            'phase_results': phase_results,
            'synthesis': synthesis,
            'execution_time_ms': execution_time,
            'timestamp': datetime.now().isoformat()
        }
        
        # Run comprehensive validation
        validation_report = self.validator.validate(results)
        results['validation'] = validation_report
        
        # Log validation summary
        if validation_report['is_complete']:
            self.logger.info("Step 2 validation passed")
        else:
            self.logger.warning(f"Step 2 validation failed: {validation_report['summary']}")
            for issue in validation_report['issues']:
                if issue['severity'] == 'error':
                    self.logger.error(f"Validation error: {issue['message']}")
        
        return results
        
    async def _create_step2_analysis(self, step1_analysis_id: str, execution_mode: str) -> str:
        """Create Step 2 analysis record."""
        # Get Step 1 analysis info
        step1_info = await self.db_connection.fetchrow(
            "SELECT name, description FROM step1_analyses WHERE id = $1",
            step1_analysis_id
        )
        
        analysis_id = str(uuid.uuid4())
        
        await self.db_connection.execute(
            """
            INSERT INTO step2_analyses 
            (id, step1_analysis_id, name, description, execution_mode)
            VALUES ($1, $2, $3, $4, $5)
            """,
            analysis_id,
            step1_analysis_id,
            f"{step1_info['name']} - Step 2",
            f"Control structure analysis for {step1_info['description']}",
            execution_mode
        )
        
        return analysis_id
        
    async def _execute_parallel_agents(self, agent_names: List[str], step2_analysis_id: str, 
                                     step1_analysis_id: str, execution_mode: str,
                                     previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute multiple agents in parallel."""
        tasks = []
        
        for agent_name in agent_names:
            cognitive_styles = self.agent_config[execution_mode].get(agent_name, [CognitiveStyle.BALANCED])
            
            for style in cognitive_styles:
                agent = self._create_agent(agent_name, style)
                task = agent.analyze(
                    step1_analysis_id=step1_analysis_id,
                    step2_analysis_id=step2_analysis_id,
                    previous_results=previous_results
                )
                tasks.append((agent_name, style, task))
                
        # Execute all tasks
        results = {}
        for agent_name, style, task in tasks:
            try:
                result = await task
                key = f"{agent_name}_{style.value}" if execution_mode == 'enhanced' else agent_name
                results[key] = result
                
                # Store agent result
                await self._store_agent_result(step2_analysis_id, result)
            except Exception as e:
                self.logger.error(f"Agent {agent_name} ({style.value}) failed: {str(e)}")
                results[f"{agent_name}_{style.value}_error"] = str(e)
                
        return results
        
    async def _execute_sequential_agents(self, agent_names: List[str], step2_analysis_id: str,
                                       step1_analysis_id: str, execution_mode: str,
                                       previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agents sequentially."""
        results = {}
        
        for agent_name in agent_names:
            cognitive_styles = self.agent_config[execution_mode].get(agent_name, [CognitiveStyle.BALANCED])
            
            agent_results = {}
            for style in cognitive_styles:
                agent = self._create_agent(agent_name, style)
                
                try:
                    result = await agent.analyze(
                        step1_analysis_id=step1_analysis_id,
                        step2_analysis_id=step2_analysis_id,
                        previous_results={**previous_results, **results}
                    )
                    
                    key = f"{agent_name}_{style.value}" if execution_mode == 'enhanced' else agent_name
                    agent_results[key] = result
                    
                    # Store agent result
                    await self._store_agent_result(step2_analysis_id, result)
                    
                except Exception as e:
                    self.logger.error(f"Agent {agent_name} ({style.value}) failed: {str(e)}")
                    agent_results[f"{agent_name}_{style.value}_error"] = str(e)
                    
            # Synthesize multiple cognitive styles if enhanced mode
            if execution_mode == 'enhanced' and len(cognitive_styles) > 1:
                synthesized = self._synthesize_cognitive_styles(agent_name, agent_results)
                results[agent_name] = synthesized
            else:
                results.update(agent_results)
                
        return results
        
    def _create_agent(self, agent_name: str, cognitive_style: CognitiveStyle):
        """Create agent instance."""
        agent_classes = {
            'control_structure_analyst': ControlStructureAnalystAgent,
            'control_action_mapping': ControlActionMappingAgent,
            'state_context_analysis': StateContextAnalysisAgent,
            'feedback_mechanism': FeedbackMechanismAgent,
            'trust_boundary': TrustBoundaryAgent,
            'process_model_analyst': ProcessModelAnalystAgent
        }
        
        agent_class = agent_classes.get(agent_name)
        if not agent_class:
            raise ValueError(f"Unknown agent: {agent_name}")
            
        return agent_class(self.model_provider, self.db_connection, cognitive_style)
        
    def _synthesize_cognitive_styles(self, agent_name: str, results: Dict[str, AgentResult]) -> AgentResult:
        """Synthesize results from multiple cognitive styles."""
        # Extract successful results
        successful_results = [r for k, r in results.items() if isinstance(r, AgentResult) and r.success]
        
        if not successful_results:
            return AgentResult(
                agent_type=agent_name,
                success=False,
                data={'error': 'All cognitive styles failed'},
                execution_time_ms=0
            )
            
        # Merge data from all successful results
        merged_data = {}
        for result in successful_results:
            for key, value in result.data.items():
                if key not in merged_data:
                    merged_data[key] = value
                elif isinstance(value, list):
                    # Merge lists, removing duplicates
                    existing = merged_data[key]
                    if isinstance(existing, list):
                        # Simple deduplication based on string representation
                        seen = {str(item) for item in existing}
                        for item in value:
                            if str(item) not in seen:
                                existing.append(item)
                                seen.add(str(item))
                                
        # Average execution time
        avg_time = sum(r.execution_time_ms for r in successful_results) // len(successful_results)
        
        return AgentResult(
            agent_type=agent_name,
            success=True,
            data=merged_data,
            execution_time_ms=avg_time,
            metadata={
                'synthesis_method': 'cognitive_merge',
                'styles_synthesized': [r.metadata.get('cognitive_style') for r in successful_results]
            }
        )
        
    def _validate_phase(self, phase_name: str, results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate phase results."""
        # For now, basic validation
        validation = {'valid': True, 'errors': []}
        
        if phase_name == 'control_structure':
            # Check for at least one controller and one process
            has_controller = False
            has_process = False
            
            for result in results.values():
                if isinstance(result, AgentResult) and result.success:
                    components = result.data.get('components', {})
                    if components.get('controllers'):
                        has_controller = True
                    if components.get('controlled_processes'):
                        has_process = True
                        
            if not has_controller:
                validation['valid'] = False
                validation['errors'].append('No controllers identified')
            if not has_process:
                validation['valid'] = False
                validation['errors'].append('No controlled processes identified')
                
        return validation
        
    async def _synthesize_results(self, step2_analysis_id: str, phase_results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize final Step 2 results."""
        synthesis = {
            'control_structure_summary': '',
            'key_controllers': [],
            'critical_control_actions': [],
            'trust_boundaries': [],
            'feedback_loops': [],
            'state_contexts': [],
            'security_concerns': []
        }
        
        # Extract control structure
        control_results = phase_results.get('control_structure', {})
        for result in control_results.values():
            if isinstance(result, AgentResult) and result.success:
                components = result.data.get('components', {})
                synthesis['control_structure_summary'] = result.data.get('summary', '')
                
                # Key controllers (high authority)
                for controller in components.get('controllers', []):
                    if controller.get('authority_level') == 'high':
                        synthesis['key_controllers'].append({
                            'identifier': controller['identifier'],
                            'name': controller['name'],
                            'controls': controller.get('controls', [])
                        })
                        
        # Extract control actions
        action_results = phase_results.get('control_actions', {})
        for result in action_results.values():
            if isinstance(result, AgentResult) and result.success:
                actions = result.data.get('control_actions', {}).get('control_actions', [])
                for action in actions:
                    if action.get('authority_level') == 'mandatory':
                        synthesis['critical_control_actions'].append({
                            'identifier': action['identifier'],
                            'name': action['action_name'],
                            'type': action['action_type'],
                            'from': action.get('controller_id'),
                            'to': action.get('controlled_process_id')
                        })
        
        # Extract feedback mechanisms
        feedback_results = phase_results.get('feedback_trust', {})
        for result in feedback_results.values():
            if isinstance(result, AgentResult) and result.success and 'feedback' in result.agent_type:
                mechanisms = result.data.get('feedback_mechanisms', [])
                for feedback in mechanisms:
                    synthesis['feedback_loops'].append({
                        'identifier': feedback['identifier'],
                        'name': feedback['feedback_name'],
                        'type': feedback['information_type'],
                        'from': feedback.get('source_process_id'),
                        'to': feedback.get('target_controller_id')
                    })
        
        # Extract trust boundaries
        for result in feedback_results.values():
            if isinstance(result, AgentResult) and result.success and 'trust' in result.agent_type:
                boundaries = result.data.get('trust_boundaries', [])
                for boundary in boundaries:
                    synthesis['trust_boundaries'].append({
                        'identifier': boundary['identifier'],
                        'name': boundary['boundary_name'],
                        'type': boundary['boundary_type'],
                        'between': [boundary.get('component_a_id'), boundary.get('component_b_id')]
                    })
        
        # Extract state contexts
        state_results = phase_results.get('state_context', {})
        for result in state_results.values():
            if isinstance(result, AgentResult) and result.success:
                contexts = result.data.get('state_contexts', [])
                for context in contexts:
                    unsafe_states = context.get('unsafe_states', [])
                    if any(state.get('severity') == 'critical' for state in unsafe_states):
                        synthesis['state_contexts'].append({
                            'control_action': context['control_action_id'],
                            'critical_unsafe_states': len([s for s in unsafe_states if s.get('severity') == 'critical']),
                            'total_unsafe_states': len(unsafe_states)
                        })
                
                # Add operational modes as security concerns
                modes = result.data.get('operational_modes', [])
                for mode in modes:
                    if mode.get('restricted_actions'):
                        synthesis['security_concerns'].append({
                            'type': 'operational_mode_restriction',
                            'mode': mode['mode_name'],
                            'restricted_actions': mode['restricted_actions'],
                            'implications': mode.get('security_implications', '')
                        })
        
        # Add key feedback mechanisms to synthesis
        synthesis['key_feedback_mechanisms'] = synthesis.pop('feedback_loops', [])
        
        # Extract process models and inadequate control scenarios
        process_model_results = phase_results.get('process_models', {})
        synthesis['process_models'] = []
        synthesis['control_algorithms'] = []
        synthesis['inadequate_control_scenarios'] = []
        
        for result in process_model_results.values():
            if isinstance(result, AgentResult) and result.success:
                # Add process models
                models = result.data.get('process_models', [])
                for model in models:
                    synthesis['process_models'].append({
                        'identifier': model['identifier'],
                        'controller_id': model.get('controller_id'),
                        'process_id': model.get('process_id'),
                        'staleness_risk': model.get('staleness_risk', 'unknown'),
                        'state_variables_count': len(model.get('state_variables', []))
                    })
                
                # Add control algorithms
                algorithms = result.data.get('control_algorithms', [])
                for alg in algorithms:
                    synthesis['control_algorithms'].append({
                        'identifier': alg['identifier'],
                        'name': alg.get('name'),
                        'controller_id': alg.get('controller_id'),
                        'constraints_count': len(alg.get('constraints', []))
                    })
                
                # Add critical inadequate control scenarios
                scenarios = result.data.get('inadequate_control_scenarios', [])
                for scenario in scenarios:
                    if scenario.get('severity') in ['high', 'critical']:
                        synthesis['inadequate_control_scenarios'].append({
                            'identifier': scenario['identifier'],
                            'name': scenario.get('name'),
                            'type': scenario.get('type'),
                            'severity': scenario.get('severity'),
                            'likelihood': scenario.get('likelihood')
                        })
        
        # Include all controllers and processes for complete picture
        all_controllers = []
        all_processes = []
        for result in control_results.values():
            if isinstance(result, AgentResult) and result.success:
                components = result.data.get('components', {})
                all_controllers.extend(components.get('controllers', []))
                all_processes.extend(components.get('controlled_processes', []))
        
        # Ensure we capture all controllers referenced in actions
        synthesis['all_controllers'] = all_controllers
        synthesis['all_processes'] = all_processes
        
        # Apply cross-reference enhancement
        enhanced_synthesis = self.synthesis_enhancer.enhance_synthesis(synthesis)
        
        return enhanced_synthesis
        
    async def _store_agent_result(self, analysis_id: str, result: AgentResult) -> None:
        """Store individual agent result."""
        await self.db_connection.execute(
            """
            INSERT INTO step2_agent_results 
            (id, analysis_id, agent_type, results, execution_time_ms)
            VALUES ($1, $2, $3, $4, $5)
            """,
            str(uuid.uuid4()),
            analysis_id,
            result.agent_type,
            json.dumps(result.dict()),
            result.execution_time_ms
        )
        
    async def _store_final_results(self, analysis_id: str, synthesis: Dict[str, Any]) -> None:
        """Store final synthesis results."""
        await self.db_connection.execute(
            """
            UPDATE step2_analyses 
            SET metadata = jsonb_build_object('synthesis', $1::jsonb),
                updated_at = NOW()
            WHERE id = $2
            """,
            json.dumps(synthesis), analysis_id
        )
