"""
STPA-Sec+ Database Models
This module provides SQLAlchemy models for the STPA-Sec+ PostgreSQL schema
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, String, Text, DateTime, Float, Integer, Boolean, 
    ForeignKey, CheckConstraint, ARRAY, JSON, Numeric, Date
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

# Step 1: System Definition & Context

class SystemDefinition(Base):
    __tablename__ = 'system_definition'
    
    id = Column(String, primary_key=True, default='system-001')
    mission_statement = Column(JSON, nullable=False)
    mission_criticality = Column(JSON)
    system_boundaries = Column(JSON)
    operational_context = Column(JSON)
    business_context = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    version = Column(Integer, default=1)

class Stakeholder(Base):
    __tablename__ = 'stakeholders'
    
    id = Column(String, primary_key=True)
    type = Column(String, CheckConstraint("type IN ('primary', 'secondary', 'threat_actor')"), nullable=False)
    name = Column(String, nullable=False)
    interests = Column(ARRAY(Text))
    capabilities = Column(ARRAY(Text))
    motivation = Column(Text)
    trust_level = Column(String, CheckConstraint("trust_level IN ('trusted', 'partially_trusted', 'untrusted')"))
    properties = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class Adversary(Base):
    __tablename__ = 'adversaries'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    type = Column(String, CheckConstraint("type IN ('nation_state', 'organized_crime', 'hacktivist', 'insider', 'opportunist')"))
    technical_sophistication = Column(String, CheckConstraint("technical_sophistication IN ('low', 'medium', 'high', 'advanced')"))
    resources = Column(String, CheckConstraint("resources IN ('minimal', 'moderate', 'significant', 'unlimited')"))
    capabilities = Column(JSON)
    primary_motivation = Column(String, CheckConstraint("primary_motivation IN ('financial', 'espionage', 'disruption', 'ideology', 'personal')"))
    objectives = Column(ARRAY(Text))
    ttps = Column(JSON)
    known_campaigns = Column(ARRAY(Text))
    target_sectors = Column(ARRAY(Text))
    properties = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    control_problems = relationship("AdversaryControlProblem", back_populates="adversary")

class ControlLoop(Base):
    __tablename__ = 'control_loops'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    purpose = Column(Text)
    controlled_process = Column(String, nullable=False)
    control_algorithm = Column(Text)
    process_model = Column(JSON)
    loop_frequency = Column(String)
    max_loop_delay = Column(String)
    model_validation = Column(JSON)
    properties = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    relationships = relationship("Relationship", back_populates="control_loop")

class Loss(Base):
    __tablename__ = 'losses'
    
    id = Column(String, primary_key=True)
    description = Column(Text, nullable=False)
    severity = Column(String, CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')"), nullable=False)
    stakeholder_refs = Column(ARRAY(String), nullable=False)
    impact_type = Column(String, CheckConstraint("impact_type IN ('safety', 'financial', 'operational', 'reputation', 'privacy')"))
    properties = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class Hazard(Base):
    __tablename__ = 'hazards'
    
    id = Column(String, primary_key=True)
    description = Column(Text, nullable=False)
    loss_refs = Column(ARRAY(String), nullable=False)
    worst_case_scenario = Column(Text)
    likelihood = Column(String, CheckConstraint("likelihood IN ('rare', 'unlikely', 'possible', 'likely', 'certain')"))
    detection_difficulty = Column(String, CheckConstraint("detection_difficulty IN ('trivial', 'easy', 'moderate', 'hard', 'extreme')"))
    properties = Column(JSON)
    created_at = Column(DateTime, default=func.now())

class Entity(Base):
    __tablename__ = 'entities'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, CheckConstraint("category IN ('human', 'software', 'hardware', 'physical', 'organizational')"))
    subcategory = Column(String)
    technology = Column(String)
    version = Column(String)
    vendor = Column(String)
    criticality = Column(String, CheckConstraint("criticality IN ('low', 'medium', 'high', 'critical')"))
    trust_level = Column(String, CheckConstraint("trust_level IN ('untrusted', 'partially_trusted', 'trusted', 'critical')"))
    exposure = Column(String, CheckConstraint("exposure IN ('internal', 'dmz', 'external', 'public')"))
    owner = Column(String)
    deployment = Column(String)
    location = Column(String)
    ai_properties = Column(JSON)
    properties = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    source_relationships = relationship("Relationship", foreign_keys="Relationship.source_id", back_populates="source")
    target_relationships = relationship("Relationship", foreign_keys="Relationship.target_id", back_populates="target")
    control_problems = relationship("AdversaryControlProblem", back_populates="entity")
    ai_layers = relationship("AIAgentLayer", back_populates="agent")

# Step 2: Control Structure

class Relationship(Base):
    __tablename__ = 'relationships'
    
    id = Column(String, primary_key=True)
    source_id = Column(String, ForeignKey('entities.id', ondelete='CASCADE'), nullable=False)
    target_id = Column(String, ForeignKey('entities.id', ondelete='CASCADE'), nullable=False)
    action = Column(String, nullable=False)
    type = Column(String, CheckConstraint("type IN ('control', 'feedback')"), nullable=False)
    control_loop_id = Column(String, ForeignKey('control_loops.id'))
    operational_modes = Column(JSON)
    protocol = Column(String)
    channel = Column(String)
    data_format = Column(String)
    timing_type = Column(String, CheckConstraint("timing_type IN ('synchronous', 'asynchronous', 'periodic', 'event_driven')"))
    frequency = Column(String)
    timeout = Column(String)
    retry_policy = Column(String)
    encryption = Column(String)
    authentication = Column(String)
    integrity_check = Column(String)
    data_sensitivity = Column(String, CheckConstraint("data_sensitivity IN ('public', 'internal', 'confidential', 'secret')"))
    data_volume = Column(String)
    properties = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    source = relationship("Entity", foreign_keys=[source_id], back_populates="source_relationships")
    target = relationship("Entity", foreign_keys=[target_id], back_populates="target_relationships")
    control_loop = relationship("ControlLoop", back_populates="relationships")
    analyses = relationship("Analysis", back_populates="rel")
    scenarios = relationship("Scenario", back_populates="rel")

class AdversaryControlProblem(Base):
    __tablename__ = 'adversary_control_problems'
    
    adversary_id = Column(String, ForeignKey('adversaries.id'), primary_key=True)
    entity_id = Column(String, ForeignKey('entities.id'), primary_key=True)
    control_capability = Column(JSON)
    
    # Relationships
    adversary = relationship("Adversary", back_populates="control_problems")
    entity = relationship("Entity", back_populates="control_problems")

# Step 3: Analyses

class Analysis(Base):
    __tablename__ = 'stpa_analyses'
    
    id = Column(String, primary_key=True)
    relationship_id = Column(String, ForeignKey('relationships.id', ondelete='CASCADE'), nullable=False)
    analysis_type = Column(String, CheckConstraint("analysis_type IN ('stpa-sec', 'stride', 'pasta', 'maestro')"), nullable=False)
    uca_not_provided = Column(JSON)
    uca_provided_causes_hazard = Column(JSON)
    uca_wrong_timing = Column(JSON)
    uca_stopped_too_soon = Column(JSON)
    stride_spoofing = Column(JSON)
    stride_tampering = Column(JSON)
    stride_repudiation = Column(JSON)
    stride_information_disclosure = Column(JSON)
    stride_denial_of_service = Column(JSON)
    stride_elevation_of_privilege = Column(JSON)
    temporal_context = Column(JSON)
    adversarial_context = Column(JSON)
    dread_assessment = Column(JSON)
    analyzed_by = Column(String)
    confidence_score = Column(Float, CheckConstraint('confidence_score >= 0 AND confidence_score <= 1'))
    properties = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    rel = relationship("Relationship", back_populates="analyses")

# Step 4: Scenarios and Mitigations

class Scenario(Base):
    __tablename__ = 'scenarios'
    
    id = Column(String, primary_key=True)
    relationship_id = Column(String, ForeignKey('relationships.id', ondelete='CASCADE'))
    uca_refs = Column(ARRAY(String))
    stride_refs = Column(ARRAY(String))
    hazard_refs = Column(ARRAY(String), nullable=False)
    threat_actor_refs = Column(ARRAY(String))
    description = Column(Text, nullable=False)
    attack_chain = Column(ARRAY(Text))
    prerequisites = Column(ARRAY(Text))
    likelihood = Column(String, CheckConstraint("likelihood IN ('rare', 'unlikely', 'possible', 'likely', 'certain')"))
    impact = Column(String, CheckConstraint("impact IN ('negligible', 'minor', 'moderate', 'major', 'catastrophic')"))
    d4_assessment = Column(JSON)
    contributing_factors = Column(JSON)
    properties = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    rel = relationship("Relationship", back_populates="scenarios")
    mitigations = relationship("ScenarioMitigation", back_populates="scenario")
    wargaming_sessions = relationship("WargamingSession", back_populates="scenario")

class Mitigation(Base):
    __tablename__ = 'mitigations'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    type = Column(String, CheckConstraint("type IN ('preventive', 'detective', 'corrective', 'compensating')"))
    category = Column(String, CheckConstraint("category IN ('technical', 'procedural', 'physical', 'administrative')"))
    effectiveness = Column(String, CheckConstraint("effectiveness IN ('low', 'medium', 'high', 'very_high')"))
    implementation_difficulty = Column(String, CheckConstraint("implementation_difficulty IN ('trivial', 'easy', 'moderate', 'hard', 'extreme')"))
    cost_estimate = Column(JSON)
    implementation_steps = Column(ARRAY(Text))
    requirements = Column(ARRAY(Text))
    side_effects = Column(ARRAY(Text))
    properties = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    scenarios = relationship("ScenarioMitigation", back_populates="mitigation")

class ScenarioMitigation(Base):
    __tablename__ = 'scenario_mitigations'
    
    scenario_id = Column(String, ForeignKey('scenarios.id', ondelete='CASCADE'), primary_key=True)
    mitigation_id = Column(String, ForeignKey('mitigations.id', ondelete='CASCADE'), primary_key=True)
    effectiveness_for_scenario = Column(String, CheckConstraint("effectiveness_for_scenario IN ('partial', 'substantial', 'complete')"))
    implementation_priority = Column(Integer, CheckConstraint('implementation_priority BETWEEN 1 AND 10'))
    notes = Column(Text)
    
    # Relationships
    scenario = relationship("Scenario", back_populates="mitigations")
    mitigation = relationship("Mitigation", back_populates="scenarios")

# STPA-Sec+ Enhancements

class AIAgentLayer(Base):
    __tablename__ = 'ai_agent_layers'
    
    agent_id = Column(String, ForeignKey('entities.id'), primary_key=True)
    layer_type = Column(String, CheckConstraint("layer_type IN ('perception', 'reasoning', 'planning', 'execution', 'learning')"), primary_key=True)
    vulnerabilities = Column(JSON)
    dependencies = Column(JSON)
    security_controls = Column(JSON)
    capability_evolution = Column(JSON)
    
    # Relationships
    agent = relationship("Entity", back_populates="ai_layers")

class DataFlow(Base):
    __tablename__ = 'data_flows'
    
    id = Column(String, primary_key=True)
    source_entity = Column(String, ForeignKey('entities.id'))
    target_entity = Column(String, ForeignKey('entities.id'))
    data_classification = Column(JSON)
    flow_properties = Column(JSON)
    purpose_limitation = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    privacy_threats = relationship("PrivacyThreat", back_populates="data_flow")

class PrivacyThreat(Base):
    __tablename__ = 'privacy_threats'
    
    id = Column(String, primary_key=True)
    relationship_id = Column(String, ForeignKey('relationships.id'))
    data_flow_id = Column(String, ForeignKey('data_flows.id'))
    linking = Column(JSON)
    identifying = Column(JSON)
    non_repudiation = Column(JSON)
    detecting = Column(JSON)
    data_disclosure = Column(JSON)
    unawareness = Column(JSON)
    non_compliance = Column(JSON)
    privacy_impact = Column(JSON)
    regulatory_context = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    data_flow = relationship("DataFlow", back_populates="privacy_threats")

class WargamingSession(Base):
    __tablename__ = 'wargaming_sessions'
    
    id = Column(String, primary_key=True)
    scenario_id = Column(String, ForeignKey('scenarios.id'))
    session_date = Column(DateTime, default=func.now())
    participants = Column(JSON)
    red_team_moves = Column(JSON)
    blue_team_responses = Column(JSON)
    effectiveness_assessment = Column(JSON)
    lessons_learned = Column(ARRAY(Text))
    recommended_improvements = Column(ARRAY(Text))
    properties = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    scenario = relationship("Scenario", back_populates="wargaming_sessions")

class ThreatLandscapeIntelligence(Base):
    __tablename__ = 'threat_landscape_intelligence'
    
    id = Column(String, primary_key=True)
    threat_category = Column(String, CheckConstraint("threat_category IN ('traditional', 'ai_ml', 'privacy', 'supply_chain', 'insider', 'nation_state')"))
    threat_name = Column(String, nullable=False)
    emergence_date = Column(Date)
    industry_relevance = Column(JSON)
    stpa_sec_plus_implications = Column(JSON)
    evolution_history = Column(JSON)
    current_variants = Column(ARRAY(Text))
    predicted_evolution = Column(ARRAY(Text))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())