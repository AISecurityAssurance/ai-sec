"""
Step 2 STPA-Sec Validation Module

Validates control structure analysis outputs to ensure completeness and consistency.
"""
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass
import logging
from enum import Enum


class ValidationSeverity(str, Enum):
    """Severity levels for validation issues"""
    ERROR = "error"      # Must fix - analysis incomplete
    WARNING = "warning"  # Should fix - analysis may be suboptimal
    INFO = "info"       # Optional - suggestions for improvement


@dataclass
class ValidationIssue:
    """Represents a validation issue found in Step 2 analysis"""
    severity: ValidationSeverity
    category: str
    message: str
    component_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class Step2Validator:
    """
    Validates Step 2 STPA-Sec control structure analysis results.
    
    Ensures:
    1. All control actions have potential UCAs identified
    2. Feedback loops are properly defined and bidirectional where appropriate
    3. Trust boundaries align with control structure hierarchy
    4. Components are properly interconnected
    5. No orphaned components exist
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def validate(self, step2_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Step 2 analysis results.
        
        Args:
            step2_results: Complete Step 2 analysis results
            
        Returns:
            Validation report with issues and completeness status
        """
        issues = []
        
        # Extract key components from results
        phase_results = step2_results.get('phase_results', {})
        synthesis = step2_results.get('synthesis', {})
        
        # Run validation checks
        issues.extend(self._validate_control_structure(phase_results, synthesis))
        issues.extend(self._validate_control_actions(phase_results, synthesis))
        issues.extend(self._validate_feedback_mechanisms(phase_results, synthesis))
        issues.extend(self._validate_trust_boundaries(phase_results, synthesis))
        issues.extend(self._validate_component_connectivity(phase_results, synthesis))
        
        # Generate summary
        error_count = sum(1 for i in issues if i.severity == ValidationSeverity.ERROR)
        warning_count = sum(1 for i in issues if i.severity == ValidationSeverity.WARNING)
        info_count = sum(1 for i in issues if i.severity == ValidationSeverity.INFO)
        
        is_complete = error_count == 0
        
        return {
            'is_complete': is_complete,
            'issues': [self._issue_to_dict(i) for i in issues],
            'summary': {
                'total_issues': len(issues),
                'errors': error_count,
                'warnings': warning_count,
                'info': info_count
            },
            'validation_status': 'passed' if is_complete else 'failed'
        }
    
    def _validate_control_structure(self, phase_results: Dict, synthesis: Dict) -> List[ValidationIssue]:
        """Validate basic control structure integrity."""
        issues = []
        
        # Check for controllers
        controllers = synthesis.get('key_controllers', [])
        if not controllers:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category='control_structure',
                message='No controllers identified in the system'
            ))
        
        # Check that each controller has at least one controlled process
        for controller in controllers:
            if not controller.get('controls'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category='control_structure',
                    message=f"Controller {controller.get('identifier')} has no controlled processes",
                    component_id=controller.get('identifier')
                ))
        
        return issues
    
    def _validate_control_actions(self, phase_results: Dict, synthesis: Dict) -> List[ValidationIssue]:
        """Validate control actions and check for UCAs."""
        issues = []
        
        # Get control actions
        control_actions = synthesis.get('critical_control_actions', [])
        
        if not control_actions:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category='control_actions',
                message='No control actions identified'
            ))
            return issues
        
        # Check each control action
        for action in control_actions:
            # Verify action has required fields
            if not action.get('from') or not action.get('to'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category='control_actions',
                    message=f"Control action {action.get('identifier')} missing from/to specification",
                    component_id=action.get('identifier')
                ))
            
            # Check for UCAs (this would need to be added to the agents)
            if not action.get('potential_ucas'):
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category='control_actions',
                    message=f"Control action {action.get('identifier')} has no identified UCAs",
                    component_id=action.get('identifier'),
                    details={
                        'recommendation': 'Consider UCAs: Not providing action, providing action, wrong timing, wrong duration'
                    }
                ))
        
        return issues
    
    def _validate_feedback_mechanisms(self, phase_results: Dict, synthesis: Dict) -> List[ValidationIssue]:
        """Validate feedback mechanisms."""
        issues = []
        
        # Get feedback mechanisms
        feedbacks = synthesis.get('key_feedback_mechanisms', [])
        
        # Build a map of control actions for bidirectional check
        control_actions = synthesis.get('critical_control_actions', [])
        action_pairs = {(a['from'], a['to']) for a in control_actions if a.get('from') and a.get('to')}
        
        # Check each feedback mechanism
        for feedback in feedbacks:
            source = feedback.get('source')
            target = feedback.get('target')
            
            if not source or not target:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category='feedback',
                    message=f"Feedback mechanism {feedback.get('identifier')} missing source/target",
                    component_id=feedback.get('identifier')
                ))
                continue
            
            # Check if there's a corresponding control action (bidirectional check)
            if (target, source) not in action_pairs:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category='feedback',
                    message=f"Feedback from {source} to {target} has no corresponding control action",
                    component_id=feedback.get('identifier'),
                    details={
                        'recommendation': 'Verify if a control action should exist in the opposite direction'
                    }
                ))
        
        # Check for control loops without feedback
        for action in control_actions:
            has_feedback = any(
                f.get('source') == action.get('to') and f.get('target') == action.get('from')
                for f in feedbacks
            )
            if not has_feedback and action.get('type') != 'emergency':
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category='feedback',
                    message=f"Control action {action.get('identifier')} has no feedback mechanism",
                    component_id=action.get('identifier'),
                    details={
                        'from': action.get('from'),
                        'to': action.get('to'),
                        'recommendation': 'Consider adding feedback for closed-loop control'
                    }
                ))
        
        return issues
    
    def _validate_trust_boundaries(self, phase_results: Dict, synthesis: Dict) -> List[ValidationIssue]:
        """Validate trust boundaries align with control structure."""
        issues = []
        
        # Get trust boundaries
        boundaries = synthesis.get('trust_boundaries', [])
        
        if not boundaries:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category='trust_boundaries',
                message='No trust boundaries identified in the system',
                details={
                    'recommendation': 'Consider boundaries between different security domains, networks, or organizations'
                }
            ))
            return issues
        
        # Get all components
        controllers = {c['identifier'] for c in synthesis.get('key_controllers', [])}
        all_components = controllers.copy()
        
        # Check boundary definitions
        for boundary in boundaries:
            components = boundary.get('components', [])
            
            if len(components) < 2:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category='trust_boundaries',
                    message=f"Trust boundary {boundary.get('identifier')} has fewer than 2 components",
                    component_id=boundary.get('identifier')
                ))
            
            # Verify components exist
            for comp in components:
                if comp not in all_components:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category='trust_boundaries',
                        message=f"Trust boundary references unknown component: {comp}",
                        component_id=boundary.get('identifier'),
                        details={'unknown_component': comp}
                    ))
        
        # Check for overlapping boundaries
        boundary_components = {}
        for boundary in boundaries:
            for comp in boundary.get('components', []):
                if comp in boundary_components:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        category='trust_boundaries',
                        message=f"Component {comp} appears in multiple trust boundaries",
                        details={
                            'boundaries': [boundary_components[comp], boundary.get('identifier')],
                            'recommendation': 'Verify if overlapping boundaries are intentional'
                        }
                    ))
                boundary_components[comp] = boundary.get('identifier')
        
        return issues
    
    def _validate_component_connectivity(self, phase_results: Dict, synthesis: Dict) -> List[ValidationIssue]:
        """Check for orphaned components and connectivity issues."""
        issues = []
        
        # Build component graph
        controllers = synthesis.get('key_controllers', [])
        control_actions = synthesis.get('critical_control_actions', [])
        feedbacks = synthesis.get('key_feedback_mechanisms', [])
        
        # Get all components
        all_components = {c['identifier'] for c in controllers}
        
        # Track connections
        connected_components = set()
        for action in control_actions:
            if action.get('from'):
                connected_components.add(action['from'])
            if action.get('to'):
                connected_components.add(action['to'])
        
        for feedback in feedbacks:
            if feedback.get('source'):
                connected_components.add(feedback['source'])
            if feedback.get('target'):
                connected_components.add(feedback['target'])
        
        # Check for orphaned controllers
        orphaned = all_components - connected_components
        for comp in orphaned:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.WARNING,
                category='connectivity',
                message=f"Controller {comp} has no connections to other components",
                component_id=comp,
                details={
                    'recommendation': 'Verify if this controller should have control actions or feedback'
                }
            ))
        
        # Check for components referenced but not defined
        referenced_not_defined = connected_components - all_components
        for comp in referenced_not_defined:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                category='connectivity',
                message=f"Component {comp} is referenced but not defined as a controller",
                component_id=comp
            ))
        
        return issues
    
    def _issue_to_dict(self, issue: ValidationIssue) -> Dict[str, Any]:
        """Convert ValidationIssue to dictionary."""
        result = {
            'severity': issue.severity.value,
            'category': issue.category,
            'message': issue.message
        }
        if issue.component_id:
            result['component_id'] = issue.component_id
        if issue.details:
            result['details'] = issue.details
        return result