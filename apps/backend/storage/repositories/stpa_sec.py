"""
STPA-Sec Repository for PostgreSQL Database Operations
Handles all database interactions for STPA-Sec analysis
"""
from typing import List, Dict, Any, Optional
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, and_, or_

from src.database.stpa_sec_models import (
    SystemDefinition, Stakeholder, Adversary, ControlLoop,
    Loss, Hazard, Entity, Relationship, Analysis, Scenario,
    Mitigation, ScenarioMitigation, AdversaryControlProblem
)
from core.models.schemas import AgentContext, AgentResult


class STPASecRepository:
    """Repository for STPA-Sec database operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def save_analysis(self, context: AgentContext, result: AgentResult) -> str:
        """Save complete STPA-Sec analysis to database"""
        analysis_id = str(uuid4())
        
        try:
            # Start transaction
            # 1. Create or update system definition
            system_id = self._save_system_definition(context, result)
            
            # 2. Save stakeholders and adversaries
            stakeholder_ids = self._save_stakeholders(result.sections.get('stakeholders', {}))
            adversary_ids = self._save_adversaries(result.sections.get('adversaries', {}))
            
            # 3. Save losses and hazards
            loss_ids = self._save_losses(result.sections.get('losses', {}), stakeholder_ids)
            hazard_ids = self._save_hazards(result.sections.get('hazards', {}), loss_ids)
            
            # 4. Save control structure
            entity_ids = self._save_entities(result.sections.get('control_structure', {}))
            relationship_ids = self._save_relationships(result.sections.get('control_structure', {}), entity_ids)
            
            # 5. Save UCAs and scenarios
            analysis_ids = self._save_analyses(result.sections.get('unsafe_control_actions', {}), relationship_ids)
            scenario_ids = self._save_scenarios(result.sections.get('loss_scenarios', {}), analysis_ids, hazard_ids)
            
            # 6. Save mitigations
            mitigation_ids = self._save_mitigations(result.sections.get('mitigations', {}), scenario_ids)
            
            # Commit transaction
            self.session.commit()
            
            return analysis_id
            
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Failed to save STPA-Sec analysis: {str(e)}")
    
    def _save_system_definition(self, context: AgentContext, result: AgentResult) -> str:
        """Save or update system definition"""
        system_def = self.session.query(SystemDefinition).filter_by(id='system-001').first()
        
        if not system_def:
            system_def = SystemDefinition(id='system-001')
        
        # Extract system info from results
        system_section = result.sections.get('system_definition', {})
        
        system_def.mission_statement = {
            "primary_mission": context.system_description[:200],  # First 200 chars as summary
            "description": context.system_description,
            "domain": context.metadata.get('system_type', 'generic') if context.metadata else 'generic',
            "purpose": system_section.get('content', {}).get('purpose', '')
        }
        
        system_def.system_boundaries = {
            "in_scope": system_section.get('content', {}).get('in_scope', []),
            "out_scope": system_section.get('content', {}).get('out_scope', []),
            "assumptions": system_section.get('content', {}).get('assumptions', [])
        }
        
        system_def.operational_context = {
            "environment": context.metadata.get('environment', {}) if context.metadata else {},
            "constraints": context.metadata.get('constraints', []) if context.metadata else [],
            "dependencies": context.metadata.get('dependencies', []) if context.metadata else []
        }
        
        self.session.add(system_def)
        self.session.flush()
        
        return system_def.id
    
    def _save_stakeholders(self, stakeholder_section: Dict[str, Any]) -> Dict[str, str]:
        """Save stakeholders from analysis"""
        stakeholder_ids = {}
        
        if not stakeholder_section:
            return stakeholder_ids
        
        stakeholders = stakeholder_section.get('content', {}).get('stakeholders', [])
        
        for stake_data in stakeholders:
            stake_id = f"stake-{uuid4().hex[:8]}"
            
            stakeholder = Stakeholder(
                id=stake_id,
                type='primary' if stake_data.get('primary', True) else 'secondary',
                name=stake_data.get('name', 'Unknown'),
                interests=stake_data.get('interests', []),
                trust_level='trusted' if stake_data.get('trusted', True) else 'partially_trusted',
                properties={
                    "description": stake_data.get('description', ''),
                    "concerns": stake_data.get('concerns', [])
                }
            )
            
            self.session.add(stakeholder)
            stakeholder_ids[stake_data.get('name', '')] = stake_id
        
        self.session.flush()
        return stakeholder_ids
    
    def _save_adversaries(self, adversary_section: Dict[str, Any]) -> Dict[str, str]:
        """Save adversaries from analysis"""
        adversary_ids = {}
        
        if not adversary_section:
            return adversary_ids
        
        adversaries = adversary_section.get('content', {}).get('adversaries', [])
        
        for adv_data in adversaries:
            adv_id = f"adv-{uuid4().hex[:8]}"
            
            adversary = Adversary(
                id=adv_id,
                name=adv_data.get('name', 'Unknown Adversary'),
                type=adv_data.get('type', 'external').lower(),
                sophistication=adv_data.get('sophistication', 'medium').lower(),
                resources=adv_data.get('resources', 'moderate').lower(),
                motivation=adv_data.get('motivation', []),
                capabilities=adv_data.get('capabilities', []),
                intent=adv_data.get('intent', []),
                access_level=adv_data.get('access_level', 'external').lower(),
                threat_rating=adv_data.get('threat_rating', 5),
                ttps={
                    "tactics": adv_data.get('tactics', []),
                    "techniques": adv_data.get('techniques', []),
                    "procedures": adv_data.get('procedures', [])
                }
            )
            
            self.session.add(adversary)
            adversary_ids[adv_data.get('name', '')] = adv_id
        
        self.session.flush()
        return adversary_ids
    
    def _save_losses(self, loss_section: Dict[str, Any], stakeholder_ids: Dict[str, str]) -> Dict[str, str]:
        """Save losses from analysis"""
        loss_ids = {}
        
        if not loss_section:
            return loss_ids
        
        losses = loss_section.get('content', {}).get('losses', [])
        
        for loss_data in losses:
            loss_id = loss_data.get('id', f"L-{uuid4().hex[:4]}")
            
            # Map stakeholder names to IDs
            stake_refs = []
            for stake_name in loss_data.get('stakeholders', []):
                if stake_name in stakeholder_ids:
                    stake_refs.append(stakeholder_ids[stake_name])
            
            loss = Loss(
                id=loss_id,
                description=loss_data.get('description', ''),
                impact_type=loss_data.get('type', 'operational').lower(),
                severity=loss_data.get('severity', 'high').lower(),
                stakeholder_refs=stake_refs,
                properties={
                    "impact_areas": loss_data.get('impact_areas', []),
                    "metrics": loss_data.get('metrics', {})
                }
            )
            
            self.session.add(loss)
            loss_ids[loss_id] = loss_id
        
        self.session.flush()
        return loss_ids
    
    def _save_hazards(self, hazard_section: Dict[str, Any], loss_ids: Dict[str, str]) -> Dict[str, str]:
        """Save hazards from analysis"""
        hazard_ids = {}
        
        if not hazard_section:
            return hazard_ids
        
        hazards = hazard_section.get('content', {}).get('hazards', [])
        
        for hazard_data in hazards:
            hazard_id = hazard_data.get('id', f"H-{uuid4().hex[:4]}")
            
            # Map loss references
            loss_refs = []
            for loss_ref in hazard_data.get('linked_losses', []):
                if loss_ref in loss_ids:
                    loss_refs.append(loss_ids[loss_ref])
            
            hazard = Hazard(
                id=hazard_id,
                description=hazard_data.get('description', ''),
                loss_refs=loss_refs,
                properties={
                    "system_state": hazard_data.get('system_state', ''),
                    "environmental_conditions": hazard_data.get('conditions', []),
                    "triggers": hazard_data.get('triggers', [])
                }
            )
            
            self.session.add(hazard)
            hazard_ids[hazard_id] = hazard_id
        
        self.session.flush()
        return hazard_ids
    
    def _save_entities(self, control_structure: Dict[str, Any]) -> Dict[str, str]:
        """Save entities from control structure"""
        entity_ids = {}
        
        if not control_structure:
            return entity_ids
        
        entities = control_structure.get('content', {}).get('entities', [])
        
        for entity_data in entities:
            entity_id = f"ent-{uuid4().hex[:8]}"
            
            # Map type to category
            entity_type = entity_data.get('type', 'controller').lower()
            category_map = {
                'controller': 'software',
                'sensor': 'hardware',
                'actuator': 'hardware',
                'human': 'human',
                'process': 'software'
            }
            
            entity = Entity(
                id=entity_id,
                name=entity_data.get('name', 'Unknown Entity'),
                category=category_map.get(entity_type, 'software'),
                description=entity_data.get('description', ''),
                properties={
                    "type": entity_type,
                    "responsibilities": entity_data.get('responsibilities', []),
                    "process_model": entity_data.get('process_model', {}),
                    "control_algorithms": entity_data.get('control_algorithms', []),
                    "interfaces": entity_data.get('interfaces', []),
                    "constraints": entity_data.get('constraints', []),
                    "assumptions": entity_data.get('assumptions', [])
                }
            )
            
            self.session.add(entity)
            entity_ids[entity_data.get('name', '')] = entity_id
        
        self.session.flush()
        return entity_ids
    
    def _save_relationships(self, control_structure: Dict[str, Any], entity_ids: Dict[str, str]) -> Dict[str, str]:
        """Save relationships between entities"""
        relationship_ids = {}
        
        if not control_structure:
            return relationship_ids
        
        relationships = control_structure.get('content', {}).get('relationships', [])
        
        for rel_data in relationships:
            rel_id = f"rel-{uuid4().hex[:8]}"
            
            # Map entity names to IDs
            source_name = rel_data.get('source', '')
            target_name = rel_data.get('target', '')
            
            if source_name not in entity_ids or target_name not in entity_ids:
                continue  # Skip if entities not found
            
            # Extract first control action as the main action
            control_actions = rel_data.get('control_actions', [])
            action = control_actions[0] if control_actions else 'control'
            
            relationship = Relationship(
                id=rel_id,
                source_id=entity_ids[source_name],
                target_id=entity_ids[target_name],
                action=action,
                type=rel_data.get('type', 'control').lower(),
                properties={
                    "description": rel_data.get('description', ''),
                    "control_actions": control_actions,
                    "feedback_info": rel_data.get('feedback_info', []),
                    "timing_constraints": rel_data.get('timing_constraints', []),
                    "data_format": rel_data.get('data_format', {}),
                    "protocols": rel_data.get('protocols', [])
                }
            )
            
            self.session.add(relationship)
            relationship_ids[rel_id] = rel_id
        
        self.session.flush()
        return relationship_ids
    
    def _save_analyses(self, uca_section: Dict[str, Any], relationship_ids: Dict[str, str]) -> Dict[str, str]:
        """Save UCA analyses"""
        analysis_ids = {}
        
        if not uca_section:
            return analysis_ids
        
        ucas = uca_section.get('content', {}).get('unsafe_control_actions', [])
        
        for uca_data in ucas:
            analysis_id = f"ana-{uuid4().hex[:8]}"
            
            # Find matching relationship
            rel_id = list(relationship_ids.keys())[0] if relationship_ids else None  # Simplified for now
            
            analysis = Analysis(
                id=analysis_id,
                relationship_id=rel_id,
                analysis_type='stpa-sec',
                uca_not_provided=uca_data.get('not_provided', {}),
                uca_provided_causes_hazard=uca_data.get('provided_causes_hazard', {}),
                uca_wrong_timing=uca_data.get('wrong_timing', {}),
                uca_stopped_too_soon=uca_data.get('stopped_too_soon', {}),
                analyzed_by='stpa-sec-agent',
                confidence_score=0.85,
                properties={
                    "context": uca_data.get('context', {}),
                    "assumptions": uca_data.get('assumptions', [])
                }
            )
            
            self.session.add(analysis)
            analysis_ids[analysis_id] = analysis_id
        
        self.session.flush()
        return analysis_ids
    
    def _save_scenarios(self, scenario_section: Dict[str, Any], analysis_ids: Dict[str, str], hazard_ids: Dict[str, str]) -> Dict[str, str]:
        """Save loss scenarios"""
        scenario_ids = {}
        
        if not scenario_section:
            return scenario_ids
        
        scenarios = scenario_section.get('content', {}).get('scenarios', [])
        
        for scenario_data in scenarios:
            scenario_id = f"scn-{uuid4().hex[:8]}"
            
            # Map hazard references
            hazard_refs = []
            for hazard_ref in scenario_data.get('hazards', []):
                if hazard_ref in hazard_ids:
                    hazard_refs.append(hazard_ids[hazard_ref])
            
            scenario = Scenario(
                id=scenario_id,
                relationship_id=list(analysis_ids.keys())[0] if analysis_ids else None,  # Simplified
                hazard_refs=hazard_refs,
                description=scenario_data.get('description', ''),
                attack_chain=scenario_data.get('attack_chain', []),
                prerequisites=scenario_data.get('prerequisites', []),
                likelihood=scenario_data.get('likelihood', 'possible').lower(),
                impact=scenario_data.get('impact', 'moderate').lower(),
                contributing_factors={
                    "technical": scenario_data.get('technical_factors', []),
                    "procedural": scenario_data.get('procedural_factors', []),
                    "environmental": scenario_data.get('environmental_factors', [])
                },
                properties=scenario_data.get('properties', {})
            )
            
            self.session.add(scenario)
            scenario_ids[scenario_id] = scenario_id
        
        self.session.flush()
        return scenario_ids
    
    def _save_mitigations(self, mitigation_section: Dict[str, Any], scenario_ids: Dict[str, str]) -> Dict[str, str]:
        """Save mitigations and link to scenarios"""
        mitigation_ids = {}
        
        if not mitigation_section:
            return mitigation_ids
        
        mitigations = mitigation_section.get('content', {}).get('mitigations', [])
        
        for mit_data in mitigations:
            mit_id = f"mit-{uuid4().hex[:8]}"
            
            mitigation = Mitigation(
                id=mit_id,
                name=mit_data.get('name', 'Unknown Mitigation'),
                description=mit_data.get('description', ''),
                type=mit_data.get('type', 'preventive').lower(),
                category=mit_data.get('category', 'technical').lower(),
                effectiveness=mit_data.get('effectiveness', 'medium').lower(),
                implementation_difficulty=mit_data.get('difficulty', 'moderate').lower(),
                cost_estimate=mit_data.get('cost_estimate', {}),
                implementation_steps=mit_data.get('steps', []),
                requirements=mit_data.get('requirements', []),
                side_effects=mit_data.get('side_effects', []),
                properties=mit_data.get('properties', {})
            )
            
            self.session.add(mitigation)
            
            # Link to scenarios
            for scenario_ref in mit_data.get('addresses_scenarios', []):
                if scenario_ref in scenario_ids:
                    link = ScenarioMitigation(
                        scenario_id=scenario_ids[scenario_ref],
                        mitigation_id=mit_id,
                        effectiveness_for_scenario=mit_data.get('effectiveness', 'substantial'),
                        implementation_priority=mit_data.get('priority', 5),
                        notes=f"Addresses {scenario_ref}"
                    )
                    self.session.add(link)
            
            mitigation_ids[mit_id] = mit_id
        
        self.session.flush()
        return mitigation_ids
    
    def get_system_definition(self) -> Optional[SystemDefinition]:
        """Get current system definition"""
        # For now, just get the first system definition
        return self.session.query(SystemDefinition).first()
    
    def get_losses_for_stakeholder(self, stakeholder_id: str) -> List[Loss]:
        """Get all losses affecting a specific stakeholder"""
        return self.session.query(Loss).filter(
            Loss.stakeholder_refs.contains([stakeholder_id])
        ).all()
    
    def get_hazards_for_loss(self, loss_id: str) -> List[Hazard]:
        """Get all hazards that could lead to a specific loss"""
        return self.session.query(Hazard).filter(
            Hazard.loss_refs.contains([loss_id])
        ).all()
    
    def get_control_structure(self) -> Dict[str, Any]:
        """Get complete control structure with entities and relationships"""
        entities = self.session.query(Entity).all()
        relationships = self.session.query(Relationship).options(
            joinedload(Relationship.source),
            joinedload(Relationship.target)
        ).all()
        
        return {
            "entities": [
                {
                    "id": e.id,
                    "name": e.name,
                    "type": e.properties.get('type', 'unknown') if e.properties else 'unknown',
                    "description": e.description,
                    "responsibilities": e.properties.get('responsibilities', []) if e.properties else []
                } for e in entities
            ],
            "relationships": [
                {
                    "id": r.id,
                    "source": r.source.name,
                    "target": r.target.name,
                    "type": r.type,
                    "control_actions": r.properties.get('control_actions', []) if r.properties else [],
                    "feedback_info": r.properties.get('feedback_info', []) if r.properties else []
                } for r in relationships
            ]
        }
    
    def get_scenarios_by_severity(self, min_risk_score: float = 0.0) -> List[Scenario]:
        """Get scenarios above a certain risk threshold"""
        return self.session.query(Scenario).filter(
            Scenario.risk_score >= min_risk_score
        ).order_by(Scenario.risk_score.desc()).all()