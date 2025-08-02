"""
Cross-reference validation for Step 2 agent outputs
"""
from typing import Dict, Any, List, Set, Tuple
import logging


class CrossReferenceValidator:
    """
    Validates cross-references between Step 2 agent outputs to ensure consistency.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validation_errors = []
        self.validation_warnings = []
        
    def validate(self, phase_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate cross-references across all agent outputs.
        
        Returns validation report with errors and warnings.
        """
        self.validation_errors = []
        self.validation_warnings = []
        
        # Extract data from phase results
        components = self._extract_components(phase_results)
        control_actions = self._extract_control_actions(phase_results)
        feedback_mechanisms = self._extract_feedback(phase_results)
        trust_boundaries = self._extract_trust_boundaries(phase_results)
        contexts = self._extract_contexts(phase_results)
        process_models = self._extract_process_models(phase_results)
        
        # Extract hierarchy information
        hierarchy = self._extract_hierarchy(phase_results)
        
        # Run validation checks
        self._validate_control_action_references(control_actions, components)
        self._validate_feedback_references(feedback_mechanisms, components)
        self._validate_trust_boundary_references(trust_boundaries, components)
        self._validate_context_references(contexts, control_actions)
        self._validate_process_model_references(process_models, components)
        self._validate_component_consistency(components, control_actions, feedback_mechanisms)
        self._validate_hierarchy_consistency(components, hierarchy)
        self._validate_process_model_completeness(components, process_models, control_actions)
        
        # Generate report
        return {
            'valid': len(self.validation_errors) == 0,
            'errors': self.validation_errors,
            'warnings': self.validation_warnings,
            'summary': self._generate_summary()
        }
    
    def _extract_components(self, phase_results: Dict[str, Any]) -> Dict[str, Set[str]]:
        """Extract all components from control structure phase."""
        components = {
            'controllers': set(),
            'processes': set(),
            'all': set()
        }
        
        control_structure = phase_results.get('control_structure', {})
        for key, result in control_structure.items():
            if hasattr(result, 'data') and result.success:
                data = result.data
            elif isinstance(result, dict) and result.get('success'):
                data = result.get('data', {})
            else:
                continue
                
            comp_data = data.get('components', {})
            for ctrl in comp_data.get('controllers', []):
                components['controllers'].add(ctrl.get('identifier'))
                components['all'].add(ctrl.get('identifier'))
            for proc in comp_data.get('controlled_processes', []):
                components['processes'].add(proc.get('identifier'))
                components['all'].add(proc.get('identifier'))
                
        return components
    
    def _extract_control_actions(self, phase_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all control actions."""
        actions = []
        
        control_actions = phase_results.get('control_actions', {})
        for key, result in control_actions.items():
            if hasattr(result, 'data') and result.success:
                data = result.data
            elif isinstance(result, dict) and result.get('success'):
                data = result.get('data', {})
            else:
                continue
                
            action_data = data.get('control_actions', {})
            if isinstance(action_data, dict):
                actions.extend(action_data.get('control_actions', []))
            elif isinstance(action_data, list):
                actions.extend(action_data)
                
        return actions
    
    def _extract_feedback(self, phase_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all feedback mechanisms."""
        feedbacks = []
        
        feedback_trust = phase_results.get('feedback_trust', {})
        for key, result in feedback_trust.items():
            if 'feedback' not in key:
                continue
                
            if hasattr(result, 'data') and result.success:
                data = result.data
            elif isinstance(result, dict) and result.get('success'):
                data = result.get('data', {})
            else:
                continue
                
            feedbacks.extend(data.get('feedback_mechanisms', []))
            
        return feedbacks
    
    def _extract_trust_boundaries(self, phase_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract all trust boundaries."""
        boundaries = []
        
        feedback_trust = phase_results.get('feedback_trust', {})
        for key, result in feedback_trust.items():
            if 'trust' not in key:
                continue
                
            if hasattr(result, 'data') and result.success:
                data = result.data
            elif isinstance(result, dict) and result.get('success'):
                data = result.get('data', {})
            else:
                continue
                
            boundaries.extend(data.get('trust_boundaries', []))
            
        return boundaries
    
    def _extract_contexts(self, phase_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract control contexts."""
        contexts = []
        
        control_context = phase_results.get('control_context', {})
        for key, result in control_context.items():
            if hasattr(result, 'data') and result.success:
                data = result.data
            elif isinstance(result, dict) and result.get('success'):
                data = result.get('data', {})
            else:
                continue
                
            contexts.extend(data.get('control_contexts', []))
            
        return contexts
    
    def _extract_process_models(self, phase_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract process models."""
        models = []
        
        process_models = phase_results.get('process_models', {})
        for key, result in process_models.items():
            if hasattr(result, 'data') and result.success:
                data = result.data
            elif isinstance(result, dict) and result.get('success'):
                data = result.get('data', {})
            else:
                continue
                
            models.extend(data.get('process_models', []))
            
        return models
    
    def _validate_control_action_references(self, actions: List[Dict[str, Any]], 
                                          components: Dict[str, Set[str]]) -> None:
        """Validate that control actions reference existing components."""
        for action in actions:
            controller_id = action.get('controller_id')
            process_id = action.get('controlled_process_id')
            action_id = action.get('identifier', 'Unknown')
            
            if controller_id and controller_id not in components['controllers']:
                self.validation_errors.append({
                    'type': 'invalid_reference',
                    'entity': 'control_action',
                    'id': action_id,
                    'message': f"Control action references non-existent controller: {controller_id}"
                })
                
            if process_id and process_id not in components['processes']:
                self.validation_errors.append({
                    'type': 'invalid_reference',
                    'entity': 'control_action',
                    'id': action_id,
                    'message': f"Control action references non-existent process: {process_id}"
                })
    
    def _validate_feedback_references(self, feedbacks: List[Dict[str, Any]], 
                                    components: Dict[str, Set[str]]) -> None:
        """Validate that feedback mechanisms reference existing components."""
        for feedback in feedbacks:
            source_id = feedback.get('source_process_id')
            target_id = feedback.get('target_controller_id')
            feedback_id = feedback.get('identifier', 'Unknown')
            
            if source_id and source_id not in components['processes']:
                self.validation_errors.append({
                    'type': 'invalid_reference',
                    'entity': 'feedback',
                    'id': feedback_id,
                    'message': f"Feedback references non-existent source process: {source_id}"
                })
                
            if target_id and target_id not in components['controllers']:
                self.validation_errors.append({
                    'type': 'invalid_reference',
                    'entity': 'feedback',
                    'id': feedback_id,
                    'message': f"Feedback references non-existent target controller: {target_id}"
                })
    
    def _validate_trust_boundary_references(self, boundaries: List[Dict[str, Any]], 
                                          components: Dict[str, Set[str]]) -> None:
        """Validate that trust boundaries reference existing components."""
        for boundary in boundaries:
            comp_a = boundary.get('component_a_id')
            comp_b = boundary.get('component_b_id')
            boundary_id = boundary.get('identifier', 'Unknown')
            
            if comp_a and comp_a not in components['all']:
                self.validation_errors.append({
                    'type': 'invalid_reference',
                    'entity': 'trust_boundary',
                    'id': boundary_id,
                    'message': f"Trust boundary references non-existent component: {comp_a}"
                })
                
            if comp_b and comp_b not in components['all']:
                self.validation_errors.append({
                    'type': 'invalid_reference',
                    'entity': 'trust_boundary',
                    'id': boundary_id,
                    'message': f"Trust boundary references non-existent component: {comp_b}"
                })
    
    def _validate_context_references(self, contexts: List[Dict[str, Any]], 
                                   actions: List[Dict[str, Any]]) -> None:
        """Validate that contexts reference existing control actions."""
        action_ids = {a.get('identifier') for a in actions if a.get('identifier')}
        
        for context in contexts:
            action_id = context.get('control_action_id')
            
            if action_id and action_id not in action_ids:
                self.validation_warnings.append({
                    'type': 'orphan_context',
                    'entity': 'control_context',
                    'message': f"Context references non-existent control action: {action_id}"
                })
    
    def _validate_process_model_references(self, models: List[Dict[str, Any]], 
                                         components: Dict[str, Set[str]]) -> None:
        """Validate that process models reference existing components."""
        for model in models:
            controller_id = model.get('controller_id')
            process_id = model.get('process_id')
            model_id = model.get('identifier', 'Unknown')
            
            if controller_id and controller_id not in components['controllers']:
                self.validation_errors.append({
                    'type': 'invalid_reference',
                    'entity': 'process_model',
                    'id': model_id,
                    'message': f"Process model references non-existent controller: {controller_id}"
                })
                
            if process_id and process_id not in components['processes']:
                self.validation_errors.append({
                    'type': 'invalid_reference',
                    'entity': 'process_model',
                    'id': model_id,
                    'message': f"Process model references non-existent process: {process_id}"
                })
    
    def _validate_component_consistency(self, components: Dict[str, Set[str]], 
                                      actions: List[Dict[str, Any]], 
                                      feedbacks: List[Dict[str, Any]]) -> None:
        """Validate overall component consistency."""
        # Check for controllers without any outgoing actions
        controllers_with_actions = {a.get('controller_id') for a in actions if a.get('controller_id')}
        orphan_controllers = components['controllers'] - controllers_with_actions
        
        for ctrl in orphan_controllers:
            self.validation_warnings.append({
                'type': 'orphan_component',
                'entity': 'controller',
                'id': ctrl,
                'message': f"Controller has no outgoing control actions"
            })
        
        # Check for processes without any incoming control
        processes_with_control = {a.get('controlled_process_id') for a in actions if a.get('controlled_process_id')}
        orphan_processes = components['processes'] - processes_with_control
        
        for proc in orphan_processes:
            self.validation_warnings.append({
                'type': 'orphan_component',
                'entity': 'process',
                'id': proc,
                'message': f"Process receives no control actions"
            })
        
        # Check for processes without feedback
        processes_with_feedback = {f.get('source_process_id') for f in feedbacks if f.get('source_process_id')}
        processes_without_feedback = components['processes'] - processes_with_feedback
        
        if len(processes_without_feedback) > 0:
            self.validation_warnings.append({
                'type': 'missing_feedback',
                'entity': 'system',
                'message': f"{len(processes_without_feedback)} processes have no feedback mechanisms"
            })
    
    def _extract_hierarchy(self, phase_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract hierarchy relationships from control structure phase."""
        hierarchy = []
        
        control_structure = phase_results.get('control_structure', {})
        for key, result in control_structure.items():
            if hasattr(result, 'data') and result.success:
                data = result.data
            elif isinstance(result, dict) and result.get('success'):
                data = result.get('data', {})
            else:
                continue
                
            # Look for hierarchy in relationships or control_hierarchy
            if 'relationships' in data:
                for rel in data['relationships']:
                    if rel.get('relationship_type') in ['supervises', 'coordinates', 'delegates']:
                        hierarchy.append({
                            'parent': rel.get('controller_id'),
                            'child': rel.get('process_id') or rel.get('subordinate_id'),
                            'type': rel.get('relationship_type')
                        })
            
            # Also check for explicit hierarchy field
            if 'hierarchy' in data and 'levels' in data['hierarchy']:
                levels = data['hierarchy']['levels']
                for i in range(len(levels) - 1):
                    for parent_id in levels[i].get('component_ids', []):
                        for child_id in levels[i + 1].get('component_ids', []):
                            hierarchy.append({
                                'parent': parent_id,
                                'child': child_id,
                                'type': 'hierarchical'
                            })
                            
        return hierarchy
    
    def _validate_hierarchy_consistency(self, components: Dict[str, Set[str]], 
                                      hierarchy: List[Dict[str, str]]) -> None:
        """Validate hierarchy consistency and check for issues."""
        # Check for circular dependencies
        for rel in hierarchy:
            if self._has_circular_dependency(rel['parent'], rel['child'], hierarchy):
                self.validation_errors.append({
                    'type': 'circular_hierarchy',
                    'entity': 'hierarchy',
                    'message': f"Circular dependency detected: {rel['parent']} -> {rel['child']}"
                })
        
        # Verify all parent-child relationships reference valid components
        for rel in hierarchy:
            parent = rel['parent']
            child = rel['child']
            
            if parent and parent not in components['all']:
                self.validation_errors.append({
                    'type': 'invalid_hierarchy_reference',
                    'entity': 'hierarchy',
                    'message': f"Hierarchy references non-existent parent: {parent}"
                })
                
            if child and child not in components['all']:
                self.validation_errors.append({
                    'type': 'invalid_hierarchy_reference', 
                    'entity': 'hierarchy',
                    'message': f"Hierarchy references non-existent child: {child}"
                })
        
        # Check hierarchy levels are properly assigned
        controllers_with_levels = set()
        for rel in hierarchy:
            if rel['parent'] in components['controllers']:
                controllers_with_levels.add(rel['parent'])
                
        orphan_controllers = components['controllers'] - controllers_with_levels
        if orphan_controllers:
            self.validation_warnings.append({
                'type': 'missing_hierarchy',
                'entity': 'hierarchy',
                'message': f"{len(orphan_controllers)} controllers not in hierarchy"
            })
    
    def _has_circular_dependency(self, start: str, current: str, 
                                hierarchy: List[Dict[str, str]], 
                                visited: Set[str] = None) -> bool:
        """Check for circular dependencies in hierarchy."""
        if visited is None:
            visited = set()
            
        if current in visited:
            return current == start
            
        visited.add(current)
        
        for rel in hierarchy:
            if rel['parent'] == current:
                if self._has_circular_dependency(start, rel['child'], hierarchy, visited):
                    return True
                    
        return False
    
    def _validate_process_model_completeness(self, components: Dict[str, Set[str]], 
                                            process_models: List[Dict[str, Any]],
                                            control_actions: List[Dict[str, Any]]) -> None:
        """Validate that every controller has adequate process models."""
        # Build a map of controllers to their process models
        controller_models = {}
        for model in process_models:
            controller_id = model.get('controller_id')
            if controller_id:
                if controller_id not in controller_models:
                    controller_models[controller_id] = []
                controller_models[controller_id].append(model)
        
        # Check each controller has at least one process model
        for controller_id in components['controllers']:
            if controller_id not in controller_models:
                self.validation_warnings.append({
                    'type': 'missing_process_model',
                    'entity': 'controller',
                    'id': controller_id,
                    'message': f"Controller {controller_id} has no process models"
                })
        
        # Build map of controller -> controlled processes
        controller_processes = {}
        for action in control_actions:
            controller_id = action.get('controller_id')
            process_id = action.get('controlled_process_id')
            if controller_id and process_id:
                if controller_id not in controller_processes:
                    controller_processes[controller_id] = set()
                controller_processes[controller_id].add(process_id)
        
        # Check controllers have models for their controlled processes
        for controller_id, models in controller_models.items():
            controlled = controller_processes.get(controller_id, set())
            modeled = {m.get('process_id') for m in models if m.get('process_id')}
            
            unmodeled = controlled - modeled
            if unmodeled:
                self.validation_warnings.append({
                    'type': 'incomplete_process_models',
                    'entity': 'controller',
                    'id': controller_id,
                    'message': f"Controller {controller_id} lacks models for processes: {', '.join(unmodeled)}"
                })
        
        # Check for process models without corresponding control actions
        for model in process_models:
            controller_id = model.get('controller_id')
            process_id = model.get('process_id')
            
            if controller_id and process_id:
                has_action = any(
                    a.get('controller_id') == controller_id and 
                    a.get('controlled_process_id') == process_id 
                    for a in control_actions
                )
                
                if not has_action:
                    self.validation_warnings.append({
                        'type': 'orphan_process_model',
                        'entity': 'process_model',
                        'id': model.get('identifier', 'Unknown'),
                        'message': f"Process model exists but no control action from {controller_id} to {process_id}"
                    })
    
    def _generate_summary(self) -> str:
        """Generate validation summary."""
        if not self.validation_errors and not self.validation_warnings:
            return "All cross-references valid"
        
        summary_parts = []
        if self.validation_errors:
            summary_parts.append(f"{len(self.validation_errors)} errors")
        if self.validation_warnings:
            summary_parts.append(f"{len(self.validation_warnings)} warnings")
            
        return f"Cross-reference validation: {', '.join(summary_parts)}"