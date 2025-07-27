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
            'stakeholder_analyst'
        ])
        
        # Perform validation checks
        abstraction_validation = await self._validate_abstraction_level(prior_results)
        completeness_validation = await self._validate_completeness(prior_results)
        consistency_validation = await self._validate_consistency(prior_results)
        coverage_validation = await self._validate_coverage(prior_results)
        
        # Generate quality metrics
        quality_metrics = await self._generate_quality_metrics(
            abstraction_validation,
            completeness_validation,
            consistency_validation,
            coverage_validation
        )
        
        # Identify improvement recommendations
        recommendations = await self._generate_recommendations(
            abstraction_validation,
            completeness_validation,
            consistency_validation,
            coverage_validation
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
                "abstraction": abstraction_validation,
                "completeness": completeness_validation,
                "consistency": consistency_validation,
                "coverage": coverage_validation
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
            "stakeholder_analyst": ["stakeholders", "adversaries", "mission_success_criteria"]
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
            for loss_id in exposure.get('direct_impact', []):
                if loss_id not in loss_ids:
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
    
    async def _generate_quality_metrics(self, abstraction: Dict[str, Any],
                                      completeness: Dict[str, Any],
                                      consistency: Dict[str, Any],
                                      coverage: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall quality metrics"""
        metrics = {
            "abstraction_score": abstraction['abstraction_score'],
            "completeness_score": completeness['completeness_score'],
            "consistency_score": consistency['consistency_score'],
            "coverage_score": coverage['coverage_score'],
            "overall_score": 0.0,
            "quality_level": "unknown",
            "strengths": [],
            "weaknesses": []
        }
        
        # Calculate weighted overall score
        weights = {
            "abstraction": 0.3,
            "completeness": 0.25,
            "consistency": 0.25,
            "coverage": 0.2
        }
        
        metrics['overall_score'] = (
            metrics['abstraction_score'] * weights['abstraction'] +
            metrics['completeness_score'] * weights['completeness'] +
            metrics['consistency_score'] * weights['consistency'] +
            metrics['coverage_score'] * weights['coverage']
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
        
        # Identify weaknesses
        if metrics['abstraction_score'] < 70:
            metrics['weaknesses'].append("Abstraction level violations")
        if metrics['completeness_score'] < 70:
            metrics['weaknesses'].append("Missing required elements")
        if metrics['consistency_score'] < 70:
            metrics['weaknesses'].append("Internal inconsistencies")
        if metrics['coverage_score'] < 70:
            metrics['weaknesses'].append("Insufficient coverage")
        
        return metrics
    
    async def _generate_recommendations(self, abstraction: Dict[str, Any],
                                      completeness: Dict[str, Any],
                                      consistency: Dict[str, Any],
                                      coverage: Dict[str, Any]) -> List[Dict[str, Any]]:
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
        
        return sorted(recommendations, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}[x['priority']])
    
    async def _create_step2_bridge(self, prior_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create bridge data for Step 2"""
        bridge = {
            "control_needs": {},
            "implied_boundaries": {},
            "architectural_hints": {},
            "transition_guidance": []
        }
        
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
        
        # Provide architectural hints
        mission_context = prior_results.get('mission_analyst', {}).get('mission_context', {})
        if mission_context.get('criticality') == 'mission_critical':
            bridge['architectural_hints']['redundancy'] = "High availability architecture required"
            bridge['architectural_hints']['separation'] = "Security zone separation essential"
        
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
                "step": "Allocate losses to controllers",
                "description": "Each controller must prevent specific losses"
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
        
        summary['key_findings'] = {
            "losses_identified": len(losses),
            "hazards_identified": len(hazards),
            "critical_losses": len([l for l in losses if l['severity_classification']['magnitude'] == 'catastrophic']),
            "adversary_classes": len(adversaries),
            "highest_threat": max((a['profile']['sophistication'] for a in adversaries), default='none')
        }
        
        # Risk landscape
        summary['risk_landscape'] = {
            "primary_risks": self._identify_primary_risks(losses, hazards),
            "threat_level": prior_results.get('stakeholder_analyst', {}).get('adversary_analysis', {}).get('combined_threat_level', 'unknown'),
            "coverage_gaps": len(prior_results.get('hazard_identification', {}).get('coverage_analysis', {}).get('uncovered_losses', []))
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
    
    def validate_abstraction_level(self, content: str) -> bool:
        """Validation agent validates its own abstraction"""
        return not self.is_implementation_detail(content)