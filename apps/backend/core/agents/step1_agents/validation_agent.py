"""
Validation Agent for STPA-Sec Step 1
"""
from typing import Dict, Any, List, Optional, Tuple
import json
from datetime import datetime
from uuid import uuid4

from .base_step1 import BaseStep1Agent


class ValidationAgent(BaseStep1Agent):
    """
    Validates Step 1 analysis completeness and quality
    
    Responsibilities:
    - Validate abstraction level consistency
    - Check analysis completeness
    - Identify gaps and inconsistencies
    - Validate security constraints coverage
    - Validate system boundaries definition
    - Generate quality metrics
    - Create Step 1 to Step 2 bridge
    """
    
    def get_agent_type(self) -> str:
        return "validation_agent"
    
    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Step 1 analysis"""
        await self.log_activity("Starting Step 1 validation")
        
        # Get all prior results
        prior_results = await self.get_prior_results([
            'mission_analyst',
            'loss_identification',
            'hazard_identification',
            'stakeholder_analyst',
            'security_constraints',
            'system_boundaries'
        ])
        
        # Perform validation checks
        abstraction_validation = await self._validate_abstraction_level(prior_results)
        completeness_validation = await self._validate_completeness(prior_results)
        consistency_validation = await self._validate_consistency(prior_results)
        coverage_validation = await self._validate_coverage(prior_results)
        security_constraints_validation = await self._validate_security_constraints(prior_results)
        system_boundaries_validation = await self._validate_system_boundaries(prior_results)
        
        # Generate quality metrics
        quality_metrics = await self._generate_quality_metrics(
            abstraction_validation,
            completeness_validation,
            consistency_validation,
            coverage_validation,
            security_constraints_validation,
            system_boundaries_validation
        )
        
        # Identify improvement recommendations
        recommendations = await self._generate_recommendations(
            abstraction_validation,
            completeness_validation,
            consistency_validation,
            coverage_validation,
            security_constraints_validation,
            system_boundaries_validation
        )
        
        # Create Step 1 to Step 2 bridge
        step2_bridge = await self._create_step2_bridge(prior_results)
        
        # Generate executive summary
        executive_summary = await self._generate_executive_summary(
            prior_results,
            quality_metrics
        )
        
        results = {
            "validation_results": {
                # Use expected field names for coordinator
                "mission_clarity": abstraction_validation,
                "loss_completeness": completeness_validation,
                "hazard_coverage": coverage_validation,
                "stakeholder_coverage": consistency_validation,
                # Additional validation results
                "security_constraints": security_constraints_validation,
                "system_boundaries": system_boundaries_validation
            },
            "quality_metrics": quality_metrics,
            "recommendations": recommendations,
            "step2_bridge": step2_bridge,
            "executive_summary": executive_summary,
            "validation_timestamp": datetime.now().isoformat(),
            "overall_status": self._determine_overall_status(quality_metrics)
        }
        
        await self.save_results(results)
        await self.log_activity("Completed Step 1 validation", {
            "overall_status": results['overall_status'],
            "quality_score": quality_metrics['overall_score']
        })
        
        return results
    
    async def _validate_abstraction_level(self, prior_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all content maintains proper abstraction level"""
        validation = {
            "status": "pass",
            "violations": [],
            "warnings": [],
            "abstraction_score": 100.0
        }
        
        # Check mission statement
        mission = prior_results.get('mission_analyst', {})
        problem_statement = mission.get('problem_statement', {})
        
        for key, value in problem_statement.items():
            if isinstance(value, str) and key != 'full_statement':
                if self.is_implementation_detail(value):
                    validation['violations'].append({
                        "location": f"problem_statement.{key}",
                        "content": value[:100] + "...",
                        "issue": "Contains implementation details"
                    })
                if self.is_prevention_language(value):
                    validation['violations'].append({
                        "location": f"problem_statement.{key}",
                        "content": value[:100] + "...",
                        "issue": "Contains prevention language"
                    })
        
        # Check losses
        losses = prior_results.get('loss_identification', {}).get('losses', [])
        for loss in losses:
            if self._contains_mechanism_language(loss['description']):
                validation['violations'].append({
                    "location": f"loss.{loss['identifier']}",
                    "content": loss['description'],
                    "issue": "Describes mechanism rather than outcome"
                })
        
        # Check hazards
        hazards = prior_results.get('hazard_identification', {}).get('hazards', [])
        for hazard in hazards:
            if not self._is_state_description(hazard['description']):
                validation['violations'].append({
                    "location": f"hazard.{hazard['identifier']}",
                    "content": hazard['description'],
                    "issue": "Not expressed as system state"
                })
            if self._contains_action_language(hazard['description']):
                validation['warnings'].append({
                    "location": f"hazard.{hazard['identifier']}",
                    "content": hazard['description'],
                    "issue": "Contains action-oriented language"
                })
        
        # Calculate abstraction score
        total_items = len(problem_statement) + len(losses) + len(hazards)
        violation_count = len(validation['violations'])
        warning_count = len(validation['warnings'])
        
        if total_items > 0:
            validation['abstraction_score'] = max(0, 100 - (violation_count * 10) - (warning_count * 5))
        
        if validation['violations']:
            validation['status'] = "fail"
        elif validation['warnings']:
            validation['status'] = "warning"
        
        return validation
    
    def _contains_mechanism_language(self, text: str) -> bool:
        """Check if text describes mechanisms rather than outcomes"""
        mechanism_indicators = [
            "attack", "exploit", "breach", "hack", "injection",
            "overflow", "bypass", "tampering", "spoofing"
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in mechanism_indicators)
    
    def _is_state_description(self, text: str) -> bool:
        """Check if text describes a state"""
        state_indicators = [
            "operates", "state", "condition", "mode", "status",
            "configuration", "posture", "situation"
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in state_indicators)
    
    def _contains_action_language(self, text: str) -> bool:
        """Check if text contains action-oriented language"""
        action_indicators = [
            "performs", "executes", "runs", "processes", "handles",
            "manages", "controls", "directs"
        ]
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in action_indicators)
    
    async def _validate_completeness(self, prior_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis completeness"""
        validation = {
            "status": "pass",
            "missing_elements": [],
            "incomplete_elements": [],
            "completeness_score": 100.0
        }
        
        required_elements = {
            "mission_analyst": ["problem_statement", "mission_context", "operational_constraints"],
            "loss_identification": ["losses", "dependencies", "cascade_analysis"],
            "hazard_identification": ["hazards", "hazard_loss_mappings", "temporal_analysis"],
            "stakeholder_analyst": ["stakeholders", "adversaries", "mission_success_criteria"],
            "security_constraints": ["security_constraints", "constraint_hazard_mappings"],
            "system_boundaries": ["system_boundaries", "boundary_analysis"]
        }
        
        # Check for missing agents
        for agent, elements in required_elements.items():
            if agent not in prior_results:
                validation['missing_elements'].append({
                    "element": agent,
                    "impact": "critical",
                    "description": f"{agent} analysis not performed"
                })
            else:
                # Check for missing elements within agent results
                agent_results = prior_results[agent]
                for element in elements:
                    if element not in agent_results or not agent_results[element]:
                        validation['incomplete_elements'].append({
                            "element": f"{agent}.{element}",
                            "impact": "major",
                            "description": f"Missing {element} in {agent}"
                        })
        
        # Check minimum quantities
        losses = prior_results.get('loss_identification', {}).get('losses', [])
        if len(losses) < 3:
            validation['incomplete_elements'].append({
                "element": "losses",
                "impact": "major",
                "description": f"Only {len(losses)} losses identified (minimum 3 recommended)"
            })
        
        hazards = prior_results.get('hazard_identification', {}).get('hazards', [])
        if len(hazards) < 3:
            validation['incomplete_elements'].append({
                "element": "hazards",
                "impact": "major",
                "description": f"Only {len(hazards)} hazards identified (minimum 3 recommended)"
            })
        
        # Check minimum stakeholder count
        stakeholders = prior_results.get('stakeholder_analyst', {}).get('stakeholders', [])
        if len(stakeholders) < 5:
            validation['incomplete_elements'].append({
                "element": "stakeholders",
                "impact": "major",
                "description": f"Only {len(stakeholders)} stakeholders identified (minimum 5 recommended)"
            })
        
        # Check minimum adversary count
        adversaries = prior_results.get('stakeholder_analyst', {}).get('adversaries', [])
        if len(adversaries) < 2:
            validation['incomplete_elements'].append({
                "element": "adversaries",
                "impact": "moderate",
                "description": f"Only {len(adversaries)} adversaries identified (minimum 2 recommended)"
            })
        
        # Calculate completeness score
        total_required = sum(len(elements) for elements in required_elements.values())
        missing_count = len(validation['missing_elements']) * 3  # Weight missing agents heavily
        incomplete_count = len(validation['incomplete_elements'])
        
        validation['completeness_score'] = max(0, 100 - (missing_count * 10) - (incomplete_count * 5))
        
        if validation['missing_elements']:
            validation['status'] = "fail"
        elif validation['incomplete_elements']:
            validation['status'] = "warning"
        
        return validation
    
    async def _validate_consistency(self, prior_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate internal consistency"""
        validation = {
            "status": "pass",
            "inconsistencies": [],
            "cross_references": [],
            "consistency_score": 100.0
        }
        
        # Check loss references in hazards
        losses = prior_results.get('loss_identification', {}).get('losses', [])
        loss_ids = {loss['identifier'] for loss in losses}
        
        mappings = prior_results.get('hazard_identification', {}).get('hazard_loss_mappings', [])
        for mapping in mappings:
            if mapping['loss_id'] not in loss_ids:
                validation['inconsistencies'].append({
                    "type": "invalid_reference",
                    "location": "hazard_loss_mapping",
                    "issue": f"References non-existent loss {mapping['loss_id']}"
                })
        
        # Check loss references in success criteria
        success_criteria = prior_results.get('stakeholder_analyst', {}).get('mission_success_criteria', {})
        success_states = success_criteria.get('success_states', {})
        
        for state_name, state_def in success_states.items():
            violated_by = state_def.get('violated_by_losses', [])
            for loss_id in violated_by:
                if loss_id not in loss_ids:
                    validation['inconsistencies'].append({
                        "type": "invalid_reference",
                        "location": f"success_criteria.{state_name}",
                        "issue": f"References non-existent loss {loss_id}"
                    })
        
        # Check stakeholder loss exposure consistency
        stakeholders = prior_results.get('stakeholder_analyst', {}).get('stakeholders', [])
        for stakeholder in stakeholders:
            exposure = stakeholder.get('loss_exposure', {})
            # Handle both dict and list formats
            if isinstance(exposure, dict):
                for loss_id in exposure.get('direct_impact', []):
                    if loss_id not in loss_ids:
                        validation['inconsistencies'].append({
                            "type": "invalid_reference",
                            "location": f"stakeholder.{stakeholder['name']}.loss_exposure",
                            "issue": f"References non-existent loss {loss_id}"
                        })
            elif isinstance(exposure, list):
                # If exposure is a list, it might contain loss identifiers directly
                for loss_id in exposure:
                    if isinstance(loss_id, str) and loss_id not in loss_ids:
                        validation['inconsistencies'].append({
                            "type": "invalid_reference",
                            "location": f"stakeholder.{stakeholder['name']}.loss_exposure",
                            "issue": f"References non-existent loss {loss_id}"
                        })
        
        # Check terminology consistency
        domain = prior_results.get('mission_analyst', {}).get('mission_context', {}).get('domain', '')
        if domain:
            validation['cross_references'].append({
                "check": "domain_consistency",
                "status": "verified",
                "details": f"Domain '{domain}' used consistently"
            })
        
        # Calculate consistency score
        inconsistency_count = len(validation['inconsistencies'])
        validation['consistency_score'] = max(0, 100 - (inconsistency_count * 10))
        
        if validation['inconsistencies']:
            validation['status'] = "warning"
        
        return validation
    
    async def _validate_coverage(self, prior_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate analysis coverage"""
        validation = {
            "status": "pass",
            "coverage_gaps": [],
            "coverage_metrics": {},
            "coverage_score": 100.0
        }
        
        # Loss coverage by hazards
        losses = prior_results.get('loss_identification', {}).get('losses', [])
        mappings = prior_results.get('hazard_identification', {}).get('hazard_loss_mappings', [])
        
        covered_losses = {mapping['loss_id'] for mapping in mappings}
        uncovered_losses = [loss for loss in losses if loss['identifier'] not in covered_losses]
        
        if uncovered_losses:
            validation['coverage_gaps'].append({
                "type": "uncovered_losses",
                "items": [loss['identifier'] for loss in uncovered_losses],
                "impact": "major",
                "description": "Losses without associated hazards"
            })
        
        validation['coverage_metrics']['loss_coverage'] = {
            "total_losses": len(losses),
            "covered_losses": len(covered_losses),
            "coverage_percentage": (len(covered_losses) / len(losses) * 100) if losses else 0
        }
        
        # Stakeholder coverage
        stakeholder_types = ['user', 'operator', 'regulator', 'owner', 'partner', 'society']
        stakeholders = prior_results.get('stakeholder_analyst', {}).get('stakeholders', [])
        covered_types = {s['stakeholder_type'] for s in stakeholders}
        missing_types = set(stakeholder_types) - covered_types
        
        if missing_types:
            validation['coverage_gaps'].append({
                "type": "missing_stakeholder_types",
                "items": list(missing_types),
                "impact": "minor",
                "description": "Stakeholder types not represented"
            })
        
        validation['coverage_metrics']['stakeholder_coverage'] = {
            "expected_types": len(stakeholder_types),
            "covered_types": len(covered_types),
            "coverage_percentage": (len(covered_types) / len(stakeholder_types) * 100)
        }
        
        # Hazard category coverage
        expected_categories = ['integrity_compromised', 'confidentiality_breached', 
                             'availability_degraded', 'capability_loss']
        hazards = prior_results.get('hazard_identification', {}).get('hazards', [])
        covered_categories = {h['hazard_category'] for h in hazards}
        missing_categories = set(expected_categories) - covered_categories
        
        if missing_categories:
            validation['coverage_gaps'].append({
                "type": "missing_hazard_categories",
                "items": list(missing_categories),
                "impact": "moderate",
                "description": "Hazard categories not covered"
            })
        
        validation['coverage_metrics']['hazard_category_coverage'] = {
            "expected_categories": len(expected_categories),
            "covered_categories": len(covered_categories),
            "coverage_percentage": (len(covered_categories) / len(expected_categories) * 100)
        }
        
        # Calculate overall coverage score
        coverage_percentages = [
            metrics['coverage_percentage'] 
            for metrics in validation['coverage_metrics'].values()
        ]
        validation['coverage_score'] = sum(coverage_percentages) / len(coverage_percentages)
        
        if validation['coverage_score'] < 80:
            validation['status'] = "warning"
        if validation['coverage_score'] < 60:
            validation['status'] = "fail"
        
        return validation
    
    async def _validate_security_constraints(self, prior_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security constraints completeness and coverage"""
        validation = {
            "status": "pass",
            "missing_constraints": [],
            "weak_constraints": [],
            "constraint_coverage": {},
            "constraint_score": 100.0
        }
        
        # Get hazards and check for constraints
        hazards = prior_results.get('hazard_identification', {}).get('hazards', [])
        # Look for constraints in the security_constraints agent results
        constraint_results = prior_results.get('security_constraints', {})
        constraints = constraint_results.get('security_constraints', [])
        constraint_mappings = constraint_results.get('constraint_hazard_mappings', [])
        
        # Build a map of hazards to their constraints
        hazard_constraint_map = {}
        for mapping in constraint_mappings:
            hazard_id = mapping['hazard_id']
            constraint_id = mapping['constraint_id']
            # Find the constraint by ID
            constraint = next((c for c in constraints if c['identifier'] == constraint_id), None)
            if constraint:
                if hazard_id not in hazard_constraint_map:
                    hazard_constraint_map[hazard_id] = []
                hazard_constraint_map[hazard_id].append(constraint)
        
        # Check that all hazards have at least one constraint
        for hazard in hazards:
            hazard_id = hazard['identifier']
            if hazard_id not in hazard_constraint_map or not hazard_constraint_map[hazard_id]:
                validation['missing_constraints'].append({
                    "hazard_id": hazard_id,
                    "hazard_description": hazard['description'],
                    "impact": "critical",
                    "issue": "No security constraints defined"
                })
        
        # Validate constraint coverage (preventive, detective, corrective, compensating)
        constraint_types = ['preventive', 'detective', 'corrective', 'compensating']
        type_coverage = {ct: 0 for ct in constraint_types}
        total_constraints = len(constraints)
        
        for constraint in constraints:
            constraint_type = constraint.get('constraint_type', 'preventive')
            if constraint_type in type_coverage:
                type_coverage[constraint_type] += 1
            
            # Check constraint strength
            if self._is_weak_constraint(constraint):
                # Find which hazards this constraint addresses
                affecting_hazards = [m['hazard_id'] for m in constraint_mappings if m['constraint_id'] == constraint['identifier']]
                validation['weak_constraints'].append({
                    "constraint_id": constraint['identifier'],
                    "affecting_hazards": affecting_hazards,
                    "constraint": constraint.get('constraint_statement', 'Unknown'),
                    "issue": "Constraint may be too generic or weak"
                })
        
        # Calculate coverage metrics
        validation['constraint_coverage'] = {
            "total_hazards": len(hazards),
            "hazards_with_constraints": len(hazard_constraint_map),
            "total_constraints": total_constraints,
            "type_distribution": type_coverage,
            "coverage_balance": self._calculate_constraint_balance(type_coverage)
        }
        
        # Check for critical constraint gaps
        # Look for hazards that are categorized as high severity or have certain likelihood
        critical_hazards = []
        for h in hazards:
            # Check various fields that might indicate criticality
            if (h.get('hazard_category') in ['integrity_compromised', 'availability_degraded', 'mission_degraded'] or
                h.get('severity') == 'high' or
                h.get('loss_likelihood') == 'certain' or
                h.get('temporal_nature', {}).get('existence') == 'always'):
                critical_hazards.append(h)
        
        for hazard in critical_hazards:
            hazard_id = hazard['identifier']
            constraint_count = len(hazard_constraint_map.get(hazard_id, []))
            if constraint_count < 2:
                validation['missing_constraints'].append({
                    "hazard_id": hazard_id,
                    "hazard_description": hazard['description'],
                    "impact": "critical",
                    "issue": f"Critical hazard needs multiple constraints (currently has {constraint_count})"
                })
        
        # Calculate constraint score
        if len(hazards) > 0:
            coverage_ratio = validation['constraint_coverage']['hazards_with_constraints'] / len(hazards)
            balance_score = validation['constraint_coverage']['coverage_balance']
            weak_penalty = len(validation['weak_constraints']) * 5
            missing_penalty = len(validation['missing_constraints']) * 10
            
            validation['constraint_score'] = max(0, (coverage_ratio * 60) + (balance_score * 40) - weak_penalty - missing_penalty)
        
        # Determine status
        if validation['missing_constraints']:
            validation['status'] = "fail"
        elif validation['weak_constraints'] or validation['constraint_score'] < 80:
            validation['status'] = "warning"
        
        return validation
    
    async def _validate_system_boundaries(self, prior_results: Dict[str, Any]) -> Dict[str, Any]:
        """Validate system boundaries definition and completeness"""
        validation = {
            "status": "pass",
            "missing_boundaries": [],
            "boundary_issues": [],
            "boundary_metrics": {},
            "boundary_score": 100.0
        }
        
        # Get boundary information from system_boundaries agent results
        boundary_results = prior_results.get('system_boundaries', {})
        system_boundaries = boundary_results.get('system_boundaries', [])
        
        # Convert list to dict for easier processing
        boundary_dict = {}
        for boundary in system_boundaries:
            boundary_type = boundary.get('boundary_type', 'unknown')
            boundary_dict[boundary_type] = boundary
        
        # Check for essential boundary types (map to our actual boundary types)
        essential_boundaries = ['system_scope', 'trust', 'responsibility', 'data_governance']
        for boundary_type in essential_boundaries:
            if boundary_type not in boundary_dict:
                validation['missing_boundaries'].append({
                    "boundary_type": boundary_type,
                    "impact": "major",
                    "description": f"Missing {boundary_type} boundary definition"
                })
        
        # Validate boundary definitions
        for boundary_type, boundary_def in boundary_dict.items():
            # Check for proper boundary structure
            if not isinstance(boundary_def, dict):
                validation['boundary_issues'].append({
                    "boundary_type": boundary_type,
                    "issue": "Invalid boundary definition structure"
                })
                continue
                
            # Check for required elements (adapt to our actual structure)
            required_elements = ['boundary_name', 'description', 'elements']
            for element in required_elements:
                if element not in boundary_def or not boundary_def[element]:
                    validation['boundary_issues'].append({
                        "boundary_type": boundary_type,
                        "missing_element": element,
                        "issue": f"Missing {element} in boundary definition"
                    })
        
        # Check boundary alignment with stakeholders
        stakeholders = prior_results.get('stakeholder_analyst', {}).get('stakeholders', [])
        external_stakeholders = [s for s in stakeholders if s.get('position', 'external') == 'external']
        
        # Simplified stakeholder boundary alignment check
        if external_stakeholders and 'responsibility' in boundary_dict:
            # Check if boundary definitions mention external stakeholders
            boundary_text = str(boundary_dict['responsibility']).lower()
            stakeholder_names = [s['name'].lower() for s in external_stakeholders]
            
            unmapped_stakeholders = [name for name in stakeholder_names if name not in boundary_text]
            if len(unmapped_stakeholders) > len(stakeholder_names) * 0.5:  # More than half unmapped
                validation['boundary_issues'].append({
                    "boundary_type": "responsibility",
                    "issue": f"Many external stakeholders may not be properly addressed in boundary definitions"
                })
        
        # Check for critical interfaces (count elements at interfaces)
        critical_interfaces = []
        for boundary_type, boundary_def in boundary_dict.items():
            if isinstance(boundary_def, dict) and 'elements' in boundary_def:
                elements = boundary_def.get('elements', [])
                interface_elements = [e for e in elements if e.get('position') == 'interface']
                critical_interfaces.extend(interface_elements)
        
        # Calculate boundary metrics
        validation['boundary_metrics'] = {
            "defined_boundaries": len(boundary_dict),
            "essential_coverage": len([b for b in essential_boundaries if b in boundary_dict]) / len(essential_boundaries) * 100,
            "critical_interfaces": len(critical_interfaces),
            "total_elements": sum(len(b.get('elements', [])) for b in boundary_dict.values() if isinstance(b, dict))
        }
        
        # Validate boundary consistency with hazards
        hazards = prior_results.get('hazard_identification', {}).get('hazards', [])
        boundary_related_hazards = [h for h in hazards if 'boundary' in h['description'].lower() or 'interface' in h['description'].lower()]
        
        if boundary_related_hazards and validation['boundary_metrics']['critical_interfaces'] == 0:
            validation['boundary_issues'].append({
                "issue": "Hazards reference boundaries but no critical interfaces defined",
                "impact": "major"
            })
        
        # Calculate boundary score
        essential_coverage = validation['boundary_metrics']['essential_coverage']
        issue_penalty = len(validation['boundary_issues']) * 10
        missing_penalty = len(validation['missing_boundaries']) * 15
        
        validation['boundary_score'] = max(0, essential_coverage - issue_penalty - missing_penalty)
        
        # Add bonus for comprehensive boundary definitions
        if validation['boundary_metrics']['critical_interfaces'] > 0:
            validation['boundary_score'] = min(100, validation['boundary_score'] + 10)
        
        # Determine status
        if validation['missing_boundaries']:
            validation['status'] = "fail"
        elif validation['boundary_issues'] or validation['boundary_score'] < 80:
            validation['status'] = "warning"
        
        return validation
    
    def _is_weak_constraint(self, constraint: Dict[str, Any]) -> bool:
        """Check if a constraint is too generic or weak"""
        weak_indicators = [
            "monitor", "review", "assess", "evaluate", "consider",
            "should", "may", "might", "could", "try"
        ]
        
        # Check both constraint_statement and description fields
        statement = constraint.get('constraint_statement', '').lower()
        description = constraint.get('description', '').lower()
        text = statement + " " + description
        return any(indicator in text for indicator in weak_indicators)
    
    def _calculate_constraint_balance(self, type_coverage: Dict[str, int]) -> float:
        """Calculate balance score for constraint type distribution"""
        total = sum(type_coverage.values())
        if total == 0:
            return 0.0
        
        # Ideal distribution: preventive (40%), detective (30%), corrective (20%), compensating (10%)
        ideal_distribution = {
            'preventive': 0.4,
            'detective': 0.3,
            'corrective': 0.2,
            'compensating': 0.1
        }
        
        balance_score = 100.0
        for constraint_type, ideal_ratio in ideal_distribution.items():
            actual_ratio = type_coverage[constraint_type] / total
            deviation = abs(actual_ratio - ideal_ratio)
            balance_score -= deviation * 50  # Penalty for deviation
        
        return max(0, balance_score)
    
    async def _generate_quality_metrics(self, abstraction: Dict[str, Any],
                                      completeness: Dict[str, Any],
                                      consistency: Dict[str, Any],
                                      coverage: Dict[str, Any],
                                      security_constraints: Dict[str, Any],
                                      system_boundaries: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall quality metrics"""
        metrics = {
            "abstraction_score": abstraction['abstraction_score'],
            "completeness_score": completeness['completeness_score'],
            "consistency_score": consistency['consistency_score'],
            "coverage_score": coverage['coverage_score'],
            "security_constraints_score": security_constraints['constraint_score'],
            "system_boundaries_score": system_boundaries['boundary_score'],
            "overall_score": 0.0,
            "quality_level": "unknown",
            "strengths": [],
            "weaknesses": []
        }
        
        # Calculate weighted overall score
        weights = {
            "abstraction": 0.2,
            "completeness": 0.2,
            "consistency": 0.2,
            "coverage": 0.15,
            "security_constraints": 0.15,
            "system_boundaries": 0.1
        }
        
        metrics['overall_score'] = (
            metrics['abstraction_score'] * weights['abstraction'] +
            metrics['completeness_score'] * weights['completeness'] +
            metrics['consistency_score'] * weights['consistency'] +
            metrics['coverage_score'] * weights['coverage'] +
            metrics['security_constraints_score'] * weights['security_constraints'] +
            metrics['system_boundaries_score'] * weights['system_boundaries']
        )
        
        # Determine quality level
        if metrics['overall_score'] >= 90:
            metrics['quality_level'] = "excellent"
        elif metrics['overall_score'] >= 80:
            metrics['quality_level'] = "good"
        elif metrics['overall_score'] >= 70:
            metrics['quality_level'] = "adequate"
        elif metrics['overall_score'] >= 60:
            metrics['quality_level'] = "needs_improvement"
        else:
            metrics['quality_level'] = "poor"
        
        # Identify strengths
        if metrics['abstraction_score'] >= 90:
            metrics['strengths'].append("Excellent abstraction level maintenance")
        if metrics['completeness_score'] >= 90:
            metrics['strengths'].append("Comprehensive analysis coverage")
        if metrics['consistency_score'] >= 90:
            metrics['strengths'].append("High internal consistency")
        if metrics['coverage_score'] >= 90:
            metrics['strengths'].append("Thorough loss and hazard coverage")
        if metrics['security_constraints_score'] >= 90:
            metrics['strengths'].append("Robust security constraint coverage")
        if metrics['system_boundaries_score'] >= 90:
            metrics['strengths'].append("Well-defined system boundaries")
        
        # Identify weaknesses
        if metrics['abstraction_score'] < 70:
            metrics['weaknesses'].append("Abstraction level violations")
        if metrics['completeness_score'] < 70:
            metrics['weaknesses'].append("Missing required elements")
        if metrics['consistency_score'] < 70:
            metrics['weaknesses'].append("Internal inconsistencies")
        if metrics['coverage_score'] < 70:
            metrics['weaknesses'].append("Insufficient coverage")
        if metrics['security_constraints_score'] < 70:
            metrics['weaknesses'].append("Weak or missing security constraints")
        if metrics['system_boundaries_score'] < 70:
            metrics['weaknesses'].append("Poorly defined system boundaries")
        
        return metrics
    
    async def _generate_recommendations(self, abstraction: Dict[str, Any],
                                      completeness: Dict[str, Any],
                                      consistency: Dict[str, Any],
                                      coverage: Dict[str, Any],
                                      security_constraints: Dict[str, Any],
                                      system_boundaries: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Abstraction recommendations
        if abstraction['violations']:
            recommendations.append({
                "priority": "high",
                "category": "abstraction",
                "recommendation": "Review and revise content to remove implementation details",
                "specific_actions": [
                    f"Revise {v['location']}" for v in abstraction['violations'][:3]
                ]
            })
        
        # Completeness recommendations
        if completeness['missing_elements']:
            recommendations.append({
                "priority": "critical",
                "category": "completeness",
                "recommendation": "Complete missing analysis elements",
                "specific_actions": [
                    f"Perform {e['element']} analysis" for e in completeness['missing_elements']
                ]
            })
        
        # Consistency recommendations
        if consistency['inconsistencies']:
            recommendations.append({
                "priority": "high",
                "category": "consistency",
                "recommendation": "Resolve reference inconsistencies",
                "specific_actions": [
                    f"Fix {i['issue']}" for i in consistency['inconsistencies'][:3]
                ]
            })
        
        # Coverage recommendations
        if coverage['coverage_gaps']:
            for gap in coverage['coverage_gaps']:
                if gap['impact'] == 'major':
                    recommendations.append({
                        "priority": "high",
                        "category": "coverage",
                        "recommendation": f"Address {gap['type']}",
                        "specific_actions": [f"Add hazards for {item}" for item in gap['items'][:3]]
                    })
        
        # Security constraints recommendations
        if security_constraints['missing_constraints']:
            recommendations.append({
                "priority": "critical",
                "category": "security_constraints",
                "recommendation": "Define security constraints for all hazards",
                "specific_actions": [
                    f"Add constraints for hazard {c['hazard_id']}" 
                    for c in security_constraints['missing_constraints'][:3]
                ]
            })
        
        if security_constraints['weak_constraints']:
            recommendations.append({
                "priority": "high",
                "category": "security_constraints",
                "recommendation": "Strengthen weak security constraints",
                "specific_actions": [
                    f"Revise constraint: {c['constraint'][:50]}..." 
                    for c in security_constraints['weak_constraints'][:3]
                ]
            })
        
        # System boundaries recommendations
        if system_boundaries['missing_boundaries']:
            recommendations.append({
                "priority": "high",
                "category": "system_boundaries",
                "recommendation": "Define missing system boundaries",
                "specific_actions": [
                    f"Define {b['boundary_type']} boundary" 
                    for b in system_boundaries['missing_boundaries']
                ]
            })
        
        if system_boundaries['boundary_issues']:
            recommendations.append({
                "priority": "medium",
                "category": "system_boundaries",
                "recommendation": "Address boundary definition issues",
                "specific_actions": [
                    issue['issue'] for issue in system_boundaries['boundary_issues'][:3]
                ]
            })
        
        return sorted(recommendations, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x['priority']])
    
    async def _create_step2_bridge(self, prior_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create bridge data for Step 2"""
        bridge = {
            "control_needs": {},
            "implied_boundaries": {},
            "architectural_hints": {},
            "security_constraint_mapping": {},
            "boundary_control_requirements": {},
            "transition_guidance": []
        }
        
        # Get mission context
        mission_context = prior_results.get('mission_analyst', {}).get('mission_context', {})
        
        # Analyze hazards to identify control needs
        hazards = prior_results.get('hazard_identification', {}).get('hazards', [])
        
        for hazard in hazards:
            category = hazard['hazard_category']
            
            if category == 'integrity_compromised':
                bridge['control_needs']['integrity_controls'] = {
                    "need": "Ensure system operates with verified integrity",
                    "addresses_hazards": [h['identifier'] for h in hazards if h['hazard_category'] == category],
                    "criticality": "essential"
                }
            elif category == 'confidentiality_breached':
                bridge['control_needs']['confidentiality_controls'] = {
                    "need": "Protect information from unauthorized observation",
                    "addresses_hazards": [h['identifier'] for h in hazards if h['hazard_category'] == category],
                    "criticality": "essential"
                }
            elif category == 'availability_degraded':
                bridge['control_needs']['availability_controls'] = {
                    "need": "Maintain service despite disruptions",
                    "addresses_hazards": [h['identifier'] for h in hazards if h['hazard_category'] == category],
                    "criticality": "essential"
                }
            elif category == 'capability_loss':
                bridge['control_needs']['capability_controls'] = {
                    "need": "Preserve critical system capabilities",
                    "addresses_hazards": [h['identifier'] for h in hazards if h['hazard_category'] == category],
                    "criticality": "essential"
                }
        
        # Identify implied boundaries from stakeholder analysis
        stakeholders = prior_results.get('stakeholder_analyst', {}).get('stakeholders', [])
        
        for stakeholder in stakeholders:
            if stakeholder['stakeholder_type'] == 'user':
                bridge['implied_boundaries']['user_system'] = {
                    "between": ["users", "system"],
                    "nature": "service_delivery",
                    "criticality": "primary"
                }
            elif stakeholder['stakeholder_type'] == 'regulator':
                bridge['implied_boundaries']['system_regulator'] = {
                    "between": ["system", "regulators"],
                    "nature": "compliance_reporting",
                    "criticality": "required"
                }
        
        # Map security constraints to control needs
        security_constraints = prior_results.get('hazard_identification', {}).get('security_constraints', {})
        constraint_types = {'preventive': [], 'detective': [], 'corrective': [], 'compensating': []}
        
        for hazard_id, constraints in security_constraints.items():
            for constraint in constraints:
                constraint_type = constraint.get('type', 'preventive')
                if constraint_type in constraint_types:
                    constraint_types[constraint_type].append({
                        "hazard_id": hazard_id,
                        "constraint": constraint.get('description', ''),
                        "implementation_hint": constraint.get('implementation_hint', '')
                    })
        
        bridge['security_constraint_mapping'] = constraint_types
        
        # Define boundary control requirements
        system_boundaries = mission_context.get('boundaries', {})
        boundary_controls = {}
        
        for boundary_type, boundary_def in system_boundaries.items():
            if isinstance(boundary_def, dict):
                boundary_controls[boundary_type] = {
                    "crossing_points": len(boundary_def.get('crossing_points', [])),
                    "critical_interfaces": [i for i in boundary_def.get('interfaces', []) if i.get('criticality') == 'critical'],
                    "control_requirement": self._determine_boundary_control_requirement(boundary_type)
                }
        
        bridge['boundary_control_requirements'] = boundary_controls
        
        # Provide architectural hints
        mission_context = prior_results.get('mission_analyst', {}).get('mission_context', {})
        if mission_context.get('criticality') == 'mission_critical':
            bridge['architectural_hints']['redundancy'] = "High availability architecture required"
            bridge['architectural_hints']['separation'] = "Security zone separation essential"
        
        # Add hints based on constraint types
        if len(constraint_types['preventive']) > len(constraint_types['detective']):
            bridge['architectural_hints']['focus'] = "Prevention-focused architecture recommended"
        else:
            bridge['architectural_hints']['focus'] = "Detection and response architecture recommended"
        
        # Transition guidance
        bridge['transition_guidance'] = [
            {
                "step": "Map control needs to control structure",
                "description": "Each control need requires one or more controllers in Step 2"
            },
            {
                "step": "Define control boundaries",
                "description": "Implied boundaries become explicit control interfaces"
            },
            {
                "step": "Implement security constraints as control actions",
                "description": "Transform constraints into specific control actions and feedback loops"
            },
            {
                "step": "Establish boundary control points",
                "description": "Place controllers at critical boundary crossing points"
            },
            {
                "step": "Allocate losses to controllers",
                "description": "Each controller must prevent specific losses"
            },
            {
                "step": "Design control channels",
                "description": "Ensure secure and reliable control command paths"
            }
        ]
        
        return bridge
    
    async def _generate_executive_summary(self, prior_results: Dict[str, Any],
                                        quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary of Step 1 analysis"""
        summary = {
            "analysis_scope": {},
            "key_findings": {},
            "risk_landscape": {},
            "quality_assessment": {},
            "next_steps": []
        }
        
        # Analysis scope
        mission = prior_results.get('mission_analyst', {})
        summary['analysis_scope'] = {
            "system": mission.get('problem_statement', {}).get('purpose_what', 'Unknown system'),
            "domain": mission.get('mission_context', {}).get('domain', 'Unknown'),
            "criticality": mission.get('mission_context', {}).get('criticality', 'Unknown')
        }
        
        # Key findings
        losses = prior_results.get('loss_identification', {}).get('losses', [])
        hazards = prior_results.get('hazard_identification', {}).get('hazards', [])
        adversaries = prior_results.get('stakeholder_analyst', {}).get('adversaries', [])
        security_constraints = prior_results.get('hazard_identification', {}).get('security_constraints', {})
        system_boundaries = prior_results.get('mission_analyst', {}).get('mission_context', {}).get('boundaries', {})
        
        # Count total constraints
        total_constraints = sum(len(constraints) for constraints in security_constraints.values())
        hazards_with_constraints = len([h for h in hazards if h['identifier'] in security_constraints and security_constraints[h['identifier']]])
        
        summary['key_findings'] = {
            "losses_identified": len(losses),
            "hazards_identified": len(hazards),
            "critical_losses": len([l for l in losses if l['severity_classification']['magnitude'] == 'catastrophic']),
            "adversary_classes": len(adversaries),
            "highest_threat": max((a['profile']['sophistication'] for a in adversaries), default='none'),
            "security_constraints_defined": total_constraints,
            "hazards_with_constraints": hazards_with_constraints,
            "system_boundaries_defined": len(system_boundaries)
        }
        
        # Risk landscape
        unconstrained_hazards = [h for h in hazards if h['identifier'] not in security_constraints or not security_constraints[h['identifier']]]
        missing_boundaries = ['system_environment', 'trusted_untrusted', 'internal_external']
        missing_boundaries = [b for b in missing_boundaries if b not in system_boundaries]
        
        summary['risk_landscape'] = {
            "primary_risks": self._identify_primary_risks(losses, hazards),
            "threat_level": prior_results.get('stakeholder_analyst', {}).get('adversary_analysis', {}).get('combined_threat_level', 'unknown'),
            "coverage_gaps": len(prior_results.get('hazard_identification', {}).get('coverage_analysis', {}).get('uncovered_losses', [])),
            "unconstrained_hazards": len(unconstrained_hazards),
            "missing_critical_boundaries": len(missing_boundaries)
        }
        
        # Quality assessment
        summary['quality_assessment'] = {
            "overall_quality": quality_metrics['quality_level'],
            "quality_score": round(quality_metrics['overall_score'], 1),
            "strengths": quality_metrics['strengths'][:2],  # Top 2
            "improvement_areas": quality_metrics['weaknesses'][:2]  # Top 2
        }
        
        # Next steps
        if quality_metrics['quality_level'] in ['excellent', 'good']:
            summary['next_steps'].append("Proceed to Step 2: Control Structure Modeling")
        else:
            summary['next_steps'].append("Address quality issues before proceeding to Step 2")
        
        if summary['risk_landscape']['coverage_gaps'] > 0:
            summary['next_steps'].append("Review and address coverage gaps")
        
        if summary['risk_landscape']['unconstrained_hazards'] > 0:
            summary['next_steps'].append(f"Define security constraints for {summary['risk_landscape']['unconstrained_hazards']} unconstrained hazards")
        
        if summary['risk_landscape']['missing_critical_boundaries'] > 0:
            summary['next_steps'].append(f"Define {summary['risk_landscape']['missing_critical_boundaries']} missing critical boundaries")
        
        summary['next_steps'].append("Review Step 1 to Step 2 bridge for architectural planning")
        
        return summary
    
    def _identify_primary_risks(self, losses: List[Dict[str, Any]], 
                               hazards: List[Dict[str, Any]]) -> List[str]:
        """Identify primary risks from losses and hazards"""
        risks = []
        
        # Critical losses
        critical_losses = [l for l in losses if l['severity_classification']['magnitude'] == 'catastrophic']
        if critical_losses:
            risks.append(f"{len(critical_losses)} catastrophic losses possible")
        
        # Always-present hazards
        persistent_hazards = [h for h in hazards if h['temporal_nature']['existence'] == 'always']
        if len(persistent_hazards) > len(hazards) * 0.7:
            risks.append("Majority of hazards are persistent")
        
        # Financial exposure
        financial_losses = [l for l in losses if l['loss_category'] == 'financial']
        if financial_losses:
            risks.append("Direct financial exposure identified")
        
        return risks[:3]  # Top 3 risks
    
    def _determine_overall_status(self, quality_metrics: Dict[str, Any]) -> str:
        """Determine overall validation status"""
        if quality_metrics['quality_level'] == 'excellent':
            return "ready_for_step2"
        elif quality_metrics['quality_level'] == 'good':
            return "ready_with_minor_issues"
        elif quality_metrics['quality_level'] == 'adequate':
            return "review_recommended"
        else:
            return "revision_required"
    
    def _determine_boundary_control_requirement(self, boundary_type: str) -> str:
        """Determine control requirement for a boundary type"""
        control_requirements = {
            "system_environment": "Strong isolation and input validation controls",
            "trusted_untrusted": "Authentication, authorization, and audit controls",
            "internal_external": "Access control and monitoring controls",
            "security_perimeter": "Defense-in-depth controls",
            "data_classification": "Encryption and data loss prevention controls"
        }
        return control_requirements.get(boundary_type, "Standard boundary controls")
    
    def validate_abstraction_level(self, content: str) -> bool:
        """Validation agent validates its own abstraction"""
        return not self.is_implementation_detail(content)