"""
STPA-Sec+ Relationship Modeling and Validation
This module provides functions for modeling and validating relationships in the STPA-Sec+ framework
"""

from typing import List, Dict, Any, Optional, Tuple, Set
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from .stpa_sec_models import (
    Entity, Relationship, ControlLoop, Analysis, Scenario,
    Adversary, AdversaryControlProblem, Hazard, Loss, Stakeholder
)
import json
from datetime import datetime

class RelationshipValidator:
    """Validates relationships and ensures consistency across the STPA-Sec model"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def validate_relationship(self, relationship: Relationship) -> Tuple[bool, List[str]]:
        """Validate a single relationship for consistency"""
        errors = []
        
        # Check that source and target exist
        source = self.session.query(Entity).filter_by(id=relationship.source_id).first()
        target = self.session.query(Entity).filter_by(id=relationship.target_id).first()
        
        if not source:
            errors.append(f"Source entity {relationship.source_id} does not exist")
        if not target:
            errors.append(f"Target entity {relationship.target_id} does not exist")
        
        if source and target:
            # Validate relationship type based on entity categories
            if not self._validate_relationship_type(source, target, relationship):
                errors.append(f"Invalid relationship type {relationship.type} between {source.category} and {target.category}")
            
            # Validate security properties
            security_errors = self._validate_security_properties(relationship, source, target)
            errors.extend(security_errors)
            
            # Validate control loop consistency
            if relationship.control_loop_id:
                loop_errors = self._validate_control_loop_consistency(relationship)
                errors.extend(loop_errors)
        
        return len(errors) == 0, errors
    
    def _validate_relationship_type(self, source: Entity, target: Entity, relationship: Relationship) -> bool:
        """Validate that the relationship type makes sense for the entity categories"""
        # Define valid relationship patterns
        valid_patterns = {
            ('software', 'software', 'control'): True,
            ('software', 'software', 'feedback'): True,
            ('human', 'software', 'control'): True,
            ('software', 'human', 'feedback'): True,
            ('hardware', 'software', 'control'): True,
            ('software', 'hardware', 'feedback'): True,
            ('organizational', 'software', 'control'): True,
            ('software', 'organizational', 'feedback'): True,
        }
        
        pattern = (source.category, target.category, relationship.type)
        return pattern in valid_patterns
    
    def _validate_security_properties(self, relationship: Relationship, source: Entity, target: Entity) -> List[str]:
        """Validate security properties of the relationship"""
        errors = []
        
        # Check encryption requirements based on data sensitivity
        if relationship.data_sensitivity in ['confidential', 'secret']:
            if not relationship.encryption or relationship.encryption.lower() == 'none':
                errors.append(f"Relationship handling {relationship.data_sensitivity} data must have encryption")
        
        # Check authentication for external exposure
        if source.exposure == 'external' or target.exposure == 'external':
            if not relationship.authentication:
                errors.append("Relationships involving external entities must have authentication")
        
        # Validate trust level consistency
        if source.trust_level == 'untrusted' and target.trust_level == 'critical':
            if relationship.type == 'control':
                errors.append("Untrusted entity cannot have direct control over critical entity")
        
        return errors
    
    def _validate_control_loop_consistency(self, relationship: Relationship) -> List[str]:
        """Validate that the relationship is consistent with its control loop"""
        errors = []
        
        control_loop = self.session.query(ControlLoop).filter_by(id=relationship.control_loop_id).first()
        if not control_loop:
            errors.append(f"Control loop {relationship.control_loop_id} does not exist")
            return errors
        
        # Check timing consistency
        if control_loop.loop_frequency and relationship.frequency:
            # Simple check - could be more sophisticated
            if control_loop.loop_frequency == 'continuous' and relationship.timing_type == 'periodic':
                errors.append("Periodic relationship in continuous control loop")
        
        return errors

class RelationshipModeler:
    """Models complex relationships and control structures"""
    
    def __init__(self, session: Session):
        self.session = session
        self.validator = RelationshipValidator(session)
    
    def create_control_structure(self, entities: List[Dict[str, Any]], 
                               relationships: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a complete control structure with entities and relationships"""
        created_entities = []
        created_relationships = []
        errors = []
        
        # Create entities first
        for entity_data in entities:
            try:
                entity = Entity(**entity_data)
                self.session.add(entity)
                created_entities.append(entity)
            except Exception as e:
                errors.append(f"Error creating entity {entity_data.get('id')}: {str(e)}")
        
        # Flush to ensure entities are available for relationships
        self.session.flush()
        
        # Create relationships
        for rel_data in relationships:
            try:
                relationship = Relationship(**rel_data)
                is_valid, validation_errors = self.validator.validate_relationship(relationship)
                
                if is_valid:
                    self.session.add(relationship)
                    created_relationships.append(relationship)
                else:
                    errors.extend(validation_errors)
            except Exception as e:
                errors.append(f"Error creating relationship {rel_data.get('id')}: {str(e)}")
        
        if not errors:
            self.session.commit()
        else:
            self.session.rollback()
        
        return {
            'success': len(errors) == 0,
            'entities_created': len(created_entities),
            'relationships_created': len(created_relationships),
            'errors': errors
        }
    
    def analyze_control_loops(self) -> List[Dict[str, Any]]:
        """Analyze all control loops for completeness and potential issues"""
        loops = self.session.query(ControlLoop).all()
        results = []
        
        for loop in loops:
            # Get all relationships in this control loop
            relationships = self.session.query(Relationship).filter_by(control_loop_id=loop.id).all()
            
            # Analyze loop properties
            analysis = {
                'loop_id': loop.id,
                'loop_name': loop.name,
                'relationship_count': len(relationships),
                'issues': []
            }
            
            # Check for missing feedback loops
            control_relationships = [r for r in relationships if r.type == 'control']
            feedback_relationships = [r for r in relationships if r.type == 'feedback']
            
            if len(control_relationships) > 0 and len(feedback_relationships) == 0:
                analysis['issues'].append({
                    'type': 'missing_feedback',
                    'severity': 'high',
                    'description': 'Control loop has no feedback mechanisms'
                })
            
            # Check for process model staleness
            if loop.model_validation:
                last_validated = loop.model_validation.get('last_validated')
                if last_validated:
                    # Simple check - validated more than 30 days ago
                    from datetime import datetime, timedelta
                    last_date = datetime.fromisoformat(last_validated)
                    if datetime.now() - last_date > timedelta(days=30):
                        analysis['issues'].append({
                            'type': 'stale_process_model',
                            'severity': 'medium',
                            'description': 'Process model not validated in over 30 days'
                        })
            
            results.append(analysis)
        
        return results
    
    def find_critical_paths(self, start_entity_id: str, end_entity_id: str) -> List[List[str]]:
        """Find all paths between two entities through relationships"""
        paths = []
        visited = set()
        
        def dfs(current_id: str, target_id: str, path: List[str]):
            if current_id == target_id:
                paths.append(path.copy())
                return
            
            if current_id in visited:
                return
            
            visited.add(current_id)
            
            # Get all outgoing relationships
            relationships = self.session.query(Relationship).filter_by(source_id=current_id).all()
            
            for rel in relationships:
                path.append(f"{rel.id}:{rel.action}")
                dfs(rel.target_id, target_id, path)
                path.pop()
            
            visited.remove(current_id)
        
        dfs(start_entity_id, end_entity_id, [])
        return paths
    
    def analyze_adversary_influence(self, adversary_id: str) -> Dict[str, Any]:
        """Analyze the potential influence of an adversary across the system"""
        adversary = self.session.query(Adversary).filter_by(id=adversary_id).first()
        if not adversary:
            return {'error': 'Adversary not found'}
        
        # Get all entities the adversary can control
        control_problems = self.session.query(AdversaryControlProblem).filter_by(
            adversary_id=adversary_id
        ).all()
        
        influenced_entities = set()
        influenced_relationships = set()
        
        for cp in control_problems:
            influenced_entities.add(cp.entity_id)
            
            # Find all relationships involving this entity
            relationships = self.session.query(Relationship).filter(
                or_(
                    Relationship.source_id == cp.entity_id,
                    Relationship.target_id == cp.entity_id
                )
            ).all()
            
            for rel in relationships:
                influenced_relationships.add(rel.id)
                # Add connected entities
                influenced_entities.add(rel.source_id)
                influenced_entities.add(rel.target_id)
        
        # Analyze potential impact
        scenarios = self.session.query(Scenario).filter(
            Scenario.threat_actor_refs.contains([adversary_id])
        ).all()
        
        total_risk = sum(s.risk_score for s in scenarios if hasattr(s, 'risk_score') and s.risk_score)
        
        return {
            'adversary': adversary.name,
            'type': adversary.type,
            'sophistication': adversary.technical_sophistication,
            'directly_controlled_entities': len(control_problems),
            'total_influenced_entities': len(influenced_entities),
            'influenced_relationships': len(influenced_relationships),
            'associated_scenarios': len(scenarios),
            'total_risk_score': total_risk,
            'entity_details': [
                {
                    'entity_id': cp.entity_id,
                    'control_capabilities': cp.control_capability
                }
                for cp in control_problems
            ]
        }

class HazardTraceability:
    """Traces hazards through the system to understand impact"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def trace_hazard_to_stakeholders(self, hazard_id: str) -> Dict[str, Any]:
        """Trace a hazard back to affected stakeholders"""
        hazard = self.session.query(Hazard).filter_by(id=hazard_id).first()
        if not hazard:
            return {'error': 'Hazard not found'}
        
        # Get losses associated with this hazard
        losses = self.session.query(Loss).filter(
            Loss.id.in_(hazard.loss_refs)
        ).all()
        
        # Get stakeholders affected by these losses
        all_stakeholder_refs = []
        for loss in losses:
            all_stakeholder_refs.extend(loss.stakeholder_refs)
        
        unique_stakeholder_refs = list(set(all_stakeholder_refs))
        stakeholders = self.session.query(Stakeholder).filter(
            Stakeholder.id.in_(unique_stakeholder_refs)
        ).all()
        
        # Get scenarios related to this hazard
        scenarios = self.session.query(Scenario).filter(
            Scenario.hazard_refs.contains([hazard_id])
        ).all()
        
        # Get analyses that reference this hazard
        analyses = self.session.query(Analysis).filter(
            or_(
                Analysis.uca_not_provided.op('->>')('hazard_refs').contains(hazard_id),
                Analysis.uca_provided_causes_hazard.op('->>')('hazard_refs').contains(hazard_id),
                Analysis.uca_wrong_timing.op('->>')('hazard_refs').contains(hazard_id),
                Analysis.uca_stopped_too_soon.op('->>')('hazard_refs').contains(hazard_id)
            )
        ).all()
        
        return {
            'hazard': {
                'id': hazard.id,
                'description': hazard.description,
                'likelihood': hazard.likelihood,
                'worst_case': hazard.worst_case_scenario
            },
            'affected_stakeholders': [
                {
                    'id': s.id,
                    'name': s.name,
                    'type': s.type,
                    'trust_level': s.trust_level
                }
                for s in stakeholders
            ],
            'related_losses': [
                {
                    'id': l.id,
                    'description': l.description,
                    'severity': l.severity,
                    'impact_type': l.impact_type
                }
                for l in losses
            ],
            'scenarios_count': len(scenarios),
            'total_risk': sum(s.risk_score for s in scenarios if hasattr(s, 'risk_score') and s.risk_score),
            'analyses_count': len(analyses)
        }
    
    def find_unmitigated_paths(self) -> List[Dict[str, Any]]:
        """Find critical paths through the system that lack adequate mitigation"""
        # Get all high-risk scenarios without mitigation
        unmitigated_scenarios = self.session.query(Scenario).outerjoin(
            ScenarioMitigation, Scenario.id == ScenarioMitigation.scenario_id
        ).filter(
            and_(
                ScenarioMitigation.scenario_id.is_(None),
                Scenario.risk_score >= 15  # High risk threshold
            )
        ).all()
        
        results = []
        for scenario in unmitigated_scenarios:
            relationship = self.session.query(Relationship).filter_by(
                id=scenario.relationship_id
            ).first()
            
            if relationship:
                source = self.session.query(Entity).filter_by(id=relationship.source_id).first()
                target = self.session.query(Entity).filter_by(id=relationship.target_id).first()
                
                results.append({
                    'scenario_id': scenario.id,
                    'description': scenario.description,
                    'risk_score': scenario.risk_score,
                    'path': f"{source.name} -> {target.name}",
                    'action': relationship.action,
                    'relationship_type': relationship.type,
                    'hazards': scenario.hazard_refs,
                    'threat_actors': scenario.threat_actor_refs
                })
        
        return sorted(results, key=lambda x: x['risk_score'], reverse=True)

# Helper functions for common validation tasks

def validate_stakeholder_references(session: Session, stakeholder_refs: List[str]) -> Tuple[bool, List[str]]:
    """Validate that all stakeholder references exist"""
    existing_ids = [s.id for s in session.query(Stakeholder.id).filter(
        Stakeholder.id.in_(stakeholder_refs)
    ).all()]
    
    missing = set(stakeholder_refs) - set(existing_ids)
    if missing:
        return False, list(missing)
    return True, []

def validate_hazard_references(session: Session, hazard_refs: List[str]) -> Tuple[bool, List[str]]:
    """Validate that all hazard references exist"""
    existing_ids = [h.id for h in session.query(Hazard.id).filter(
        Hazard.id.in_(hazard_refs)
    ).all()]
    
    missing = set(hazard_refs) - set(existing_ids)
    if missing:
        return False, list(missing)
    return True, []

def calculate_entity_criticality_score(session: Session, entity_id: str) -> float:
    """Calculate a criticality score for an entity based on its relationships and risks"""
    entity = session.query(Entity).filter_by(id=entity_id).first()
    if not entity:
        return 0.0
    
    # Base score from entity properties
    criticality_scores = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
    base_score = criticality_scores.get(entity.criticality, 1)
    
    # Add score based on relationships
    rel_count = session.query(Relationship).filter(
        or_(
            Relationship.source_id == entity_id,
            Relationship.target_id == entity_id
        )
    ).count()
    
    # Add score based on associated risks
    scenarios = session.query(Scenario).join(
        Relationship, Scenario.relationship_id == Relationship.id
    ).filter(
        or_(
            Relationship.source_id == entity_id,
            Relationship.target_id == entity_id
        )
    ).all()
    
    risk_score = sum(s.risk_score for s in scenarios if hasattr(s, 'risk_score') and s.risk_score)
    
    # Combine scores (this is a simple formula - could be more sophisticated)
    total_score = base_score + (rel_count * 0.1) + (risk_score * 0.05)
    
    return round(total_score, 2)