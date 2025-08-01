"""
Enhanced synthesis for Step 2 with cross-referencing
"""
from typing import Dict, Any, List, Set, Tuple, Optional
from collections import defaultdict
import logging


class Step2SynthesisEnhancer:
    """
    Enhances Step 2 synthesis with cross-referencing between components.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def enhance_synthesis(self, synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance synthesis with cross-references between components.
        
        Adds:
        - Trust boundary associations to control actions
        - Feedback loop completeness for control actions
        - Component hierarchy and relationships
        - Risk mappings between boundaries and actions
        """
        # Build component maps for quick lookup
        controllers_map = {c['identifier']: c for c in synthesis.get('key_controllers', [])}
        actions_map = {a['identifier']: a for a in synthesis.get('critical_control_actions', [])}
        boundaries_map = {b['identifier']: b for b in synthesis.get('trust_boundaries', [])}
        feedback_map = self._build_feedback_map(synthesis.get('key_feedback_mechanisms', []))
        
        # Enhance control actions with cross-references
        enhanced_actions = []
        for action in synthesis.get('critical_control_actions', []):
            enhanced_action = action.copy()
            
            # Add trust boundary crossing information
            boundary_crossings = self._find_boundary_crossings(
                action, 
                synthesis.get('trust_boundaries', [])
            )
            if boundary_crossings:
                enhanced_action['crosses_boundaries'] = boundary_crossings
                enhanced_action['security_critical'] = True
            
            # Add feedback loop information
            feedback_loops = feedback_map.get((action['to'], action['from']), [])
            if feedback_loops:
                enhanced_action['feedback_mechanisms'] = feedback_loops
                enhanced_action['closed_loop'] = True
            else:
                enhanced_action['closed_loop'] = False
            
            # Add controller details
            if action.get('from') in controllers_map:
                enhanced_action['controller_details'] = {
                    'name': controllers_map[action['from']]['name'],
                    'authority': controllers_map[action['from']].get('authority_level', 'unknown')
                }
            
            enhanced_actions.append(enhanced_action)
        
        # Enhance trust boundaries with component details
        enhanced_boundaries = []
        for boundary in synthesis.get('trust_boundaries', []):
            enhanced_boundary = boundary.copy()
            
            # Find all control actions crossing this boundary
            crossing_actions = []
            for action in enhanced_actions:
                if boundary['identifier'] in action.get('crosses_boundaries', []):
                    crossing_actions.append({
                        'action_id': action['identifier'],
                        'action_name': action['name'],
                        'from': action['from'],
                        'to': action['to']
                    })
            
            enhanced_boundary['crossing_actions'] = crossing_actions
            enhanced_boundary['risk_level'] = self._assess_boundary_risk(
                enhanced_boundary, 
                crossing_actions
            )
            
            enhanced_boundaries.append(enhanced_boundary)
        
        # Build component hierarchy
        component_hierarchy = self._build_component_hierarchy(
            synthesis.get('key_controllers', []),
            enhanced_actions,
            synthesis.get('key_feedback_mechanisms', [])
        )
        
        # Create enhanced synthesis
        enhanced_synthesis = synthesis.copy()
        enhanced_synthesis['critical_control_actions'] = enhanced_actions
        enhanced_synthesis['trust_boundaries'] = enhanced_boundaries
        enhanced_synthesis['component_hierarchy'] = component_hierarchy
        
        # Add cross-reference summary
        enhanced_synthesis['cross_references'] = {
            'boundary_crossing_actions': sum(
                1 for a in enhanced_actions 
                if a.get('crosses_boundaries')
            ),
            'closed_loop_actions': sum(
                1 for a in enhanced_actions 
                if a.get('closed_loop')
            ),
            'high_risk_boundaries': sum(
                1 for b in enhanced_boundaries 
                if b.get('risk_level') == 'high'
            )
        }
        
        return enhanced_synthesis
    
    def _find_boundary_crossings(self, action: Dict[str, Any], 
                                  boundaries: List[Dict[str, Any]]) -> List[str]:
        """Find which trust boundaries a control action crosses."""
        crossings = []
        
        from_component = action.get('from')
        to_component = action.get('to')
        
        if not from_component or not to_component:
            return crossings
        
        for boundary in boundaries:
            components = set(boundary.get('components', []))
            
            # Check if action crosses this boundary
            if (from_component in components and to_component not in components) or \
               (to_component in components and from_component not in components):
                crossings.append(boundary['identifier'])
        
        return crossings
    
    def _build_feedback_map(self, feedbacks: List[Dict[str, Any]]) -> Dict[Tuple[str, str], List[Dict]]:
        """Build a map of feedback mechanisms by (source, target) pairs."""
        feedback_map = defaultdict(list)
        
        for feedback in feedbacks:
            source = feedback.get('source')
            target = feedback.get('target')
            if source and target:
                feedback_map[(source, target)].append({
                    'id': feedback['identifier'],
                    'name': feedback['name'],
                    'type': feedback.get('type', 'unknown')
                })
        
        return feedback_map
    
    def _assess_boundary_risk(self, boundary: Dict[str, Any], 
                              crossing_actions: List[Dict[str, Any]]) -> str:
        """Assess risk level of a trust boundary based on crossing actions."""
        if not crossing_actions:
            return 'low'
        
        # High risk if many actions cross or if critical actions cross
        if len(crossing_actions) > 3:
            return 'high'
        
        # Check boundary type
        if boundary.get('type') in ['network', 'organizational']:
            return 'high' if crossing_actions else 'medium'
        
        return 'medium'
    
    def _build_component_hierarchy(self, controllers: List[Dict[str, Any]],
                                   actions: List[Dict[str, Any]],
                                   feedbacks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a hierarchy of components and their relationships."""
        hierarchy = {
            'controllers': {},
            'controlled_processes': {},
            'relationships': []
        }
        
        # Build controller entries
        for controller in controllers:
            ctrl_id = controller['identifier']
            hierarchy['controllers'][ctrl_id] = {
                'name': controller['name'],
                'controls': controller.get('controls', []),
                'receives_feedback_from': [],
                'sends_commands_to': []
            }
        
        # Add relationships from actions
        for action in actions:
            from_id = action.get('from')
            to_id = action.get('to')
            
            if from_id and to_id:
                # Update controller's commands
                if from_id in hierarchy['controllers']:
                    hierarchy['controllers'][from_id]['sends_commands_to'].append(to_id)
                
                # Track controlled processes
                if to_id not in hierarchy['controlled_processes']:
                    hierarchy['controlled_processes'][to_id] = {
                        'controlled_by': [],
                        'sends_feedback_to': []
                    }
                hierarchy['controlled_processes'][to_id]['controlled_by'].append(from_id)
                
                # Add relationship
                hierarchy['relationships'].append({
                    'type': 'control_action',
                    'from': from_id,
                    'to': to_id,
                    'action': action['identifier']
                })
        
        # Add feedback relationships
        for feedback in feedbacks:
            source = feedback.get('source')
            target = feedback.get('target')
            
            if source and target:
                # Update feedback tracking
                if target in hierarchy['controllers']:
                    hierarchy['controllers'][target]['receives_feedback_from'].append(source)
                if source in hierarchy['controlled_processes']:
                    hierarchy['controlled_processes'][source]['sends_feedback_to'].append(target)
                
                # Add relationship
                hierarchy['relationships'].append({
                    'type': 'feedback',
                    'from': source,
                    'to': target,
                    'feedback': feedback['identifier']
                })
        
        return hierarchy