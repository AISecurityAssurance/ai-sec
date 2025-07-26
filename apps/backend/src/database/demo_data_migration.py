"""
Demo Data Migration
Migrates frontend demo data to PostgreSQL STPA-Sec+ schema
"""

import json
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from datetime import datetime
from .stpa_sec_models import (
    SystemDefinition, Stakeholder, Adversary, ControlLoop,
    Loss, Hazard, Entity, Relationship, Analysis, Scenario,
    Mitigation, ScenarioMitigation, AIAgentLayer, DataFlow,
    PrivacyThreat, AdversaryControlProblem
)

class DemoDataMigrator:
    """Migrates demo data from frontend format to PostgreSQL"""
    
    def __init__(self, session: Session):
        self.session = session
        self.entity_map = {}  # Maps old IDs to new IDs
        self.relationship_map = {}
        self.hazard_map = {}
        self.analysis_map = {}
        
    def migrate_all(self, demo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate all demo data to PostgreSQL"""
        results = {
            'success': True,
            'steps': [],
            'errors': []
        }
        
        try:
            # Step 1: System Definition
            self._migrate_system_definition()
            results['steps'].append('System definition created')
            
            # Step 2: Stakeholders and Adversaries
            self._migrate_stakeholders()
            results['steps'].append('Stakeholders and adversaries created')
            
            # Step 3: Losses and Hazards
            self._migrate_losses_and_hazards()
            results['steps'].append('Losses and hazards created')
            
            # Step 4: Entities
            if 'entities' in demo_data:
                self._migrate_entities(demo_data['entities'])
                results['steps'].append(f"Migrated {len(demo_data['entities'])} entities")
            
            # Step 5: Control Loops and Relationships
            if 'relationships' in demo_data:
                self._migrate_relationships(demo_data['relationships'])
                results['steps'].append(f"Migrated {len(demo_data['relationships'])} relationships")
            
            # Step 6: Analyses
            if 'analyses' in demo_data:
                self._migrate_analyses(demo_data['analyses'])
                results['steps'].append('Migrated analyses')
            
            # Step 7: Scenarios and Mitigations
            if 'scenarios' in demo_data:
                self._migrate_scenarios(demo_data['scenarios'])
                results['steps'].append('Migrated scenarios')
            
            self.session.commit()
            
        except Exception as e:
            self.session.rollback()
            results['success'] = False
            results['errors'].append(str(e))
            
        return results
    
    def _migrate_system_definition(self):
        """Create system definition for banking demo"""
        system_def = SystemDefinition(
            id='system-001',
            mission_statement={
                "purpose": "Enable secure digital banking transactions",
                "method": "Multi-factor authentication and encrypted communications",
                "goals": [
                    "Protect customer financial assets",
                    "Ensure 24/7 service availability",
                    "Maintain regulatory compliance (PCI-DSS, SOX)",
                    "Prevent fraud and unauthorized access"
                ],
                "constraints": [
                    "PCI-DSS compliance required",
                    "Sub-100ms transaction latency",
                    "Zero customer data exposure",
                    "99.99% uptime SLA"
                ]
            },
            mission_criticality={
                "primary_mission": "secure digital banking",
                "success_metrics": {
                    "transaction_availability": {"target": "99.99%", "critical_threshold": "99.9%"},
                    "data_integrity": {"target": "100%", "critical_threshold": "99.999%"},
                    "response_time": {"target": "100ms", "critical_threshold": "1000ms"},
                    "fraud_rate": {"target": "0.01%", "critical_threshold": "0.1%"}
                },
                "failure_impacts": {
                    "financial": "Up to $1M per hour downtime + regulatory fines",
                    "reputation": "Customer trust erosion, negative media coverage",
                    "regulatory": "Potential license suspension, audit failures",
                    "operational": "Manual processing required, increased support costs"
                },
                "mission_dependencies": [
                    "authentication_service",
                    "transaction_processor",
                    "fraud_detection",
                    "data_storage"
                ]
            },
            system_boundaries={
                "in_scope": [
                    "Web application",
                    "Mobile applications",
                    "API gateway",
                    "Authentication service",
                    "Transaction processing",
                    "Fraud detection system",
                    "Customer database"
                ],
                "out_of_scope": [
                    "Third-party payment processors",
                    "External credit bureaus",
                    "Bank legacy systems"
                ],
                "interfaces": [
                    "Payment processor APIs",
                    "Credit bureau APIs",
                    "Regulatory reporting systems"
                ]
            },
            operational_context={
                "deployment_environments": ["production", "staging", "disaster_recovery"],
                "geographic_scope": ["US", "EU", "APAC"],
                "regulatory_jurisdictions": ["US-Federal", "EU-GDPR", "CA-PIPEDA"],
                "integration_points": ["payment_networks", "credit_bureaus", "regulatory_reporting"],
                "user_base": {
                    "retail_customers": "1M+",
                    "business_customers": "50K+",
                    "daily_transactions": "5M+",
                    "peak_load": "1K TPS"
                }
            },
            business_context={
                "business_objectives": {
                    "primary": [
                        "increase_digital_adoption_30%",
                        "reduce_fraud_losses_50%",
                        "improve_customer_satisfaction_20%"
                    ],
                    "compliance": [
                        "maintain_pci_dss_level_1",
                        "achieve_soc2_type2",
                        "gdpr_compliance"
                    ],
                    "strategic": [
                        "mobile_first_transformation",
                        "ai_powered_fraud_detection",
                        "open_banking_readiness"
                    ]
                },
                "threat_intelligence": {
                    "industry_threats": [
                        "ransomware_targeting_financial",
                        "supply_chain_attacks",
                        "mobile_banking_trojans",
                        "business_email_compromise"
                    ],
                    "targeted_campaigns": [
                        "apt28_banking_sector",
                        "carbanak_group",
                        "fin7_operations"
                    ],
                    "threat_landscape_score": 8.5
                },
                "risk_appetite": {
                    "financial": "moderate",
                    "operational": "low",
                    "reputational": "very_low",
                    "compliance": "zero_tolerance",
                    "innovation": "moderate"
                }
            }
        )
        self.session.add(system_def)
        self.session.flush()
    
    def _migrate_stakeholders(self):
        """Create stakeholders and adversaries"""
        # Primary stakeholders
        stakeholders = [
            Stakeholder(
                id='SH-001',
                type='primary',
                name='Retail Banking Customers',
                interests=['account_security', 'service_availability', 'privacy', 'ease_of_use'],
                trust_level='trusted',
                properties={
                    'count': '1M+',
                    'priority': 'critical',
                    'segments': ['individuals', 'families', 'small_business']
                }
            ),
            Stakeholder(
                id='SH-002',
                type='primary',
                name='Bank Employees',
                interests=['system_usability', 'security_tools', 'training', 'compliance'],
                trust_level='trusted',
                properties={
                    'roles': ['tellers', 'managers', 'support_staff', 'security_team']
                }
            ),
            Stakeholder(
                id='SH-003',
                type='secondary',
                name='Regulatory Bodies',
                interests=['compliance', 'audit_trails', 'incident_reporting', 'data_protection'],
                trust_level='trusted',
                properties={
                    'agencies': ['FDIC', 'OCC', 'CFPB', 'SEC']
                }
            ),
            Stakeholder(
                id='SH-004',
                type='secondary',
                name='Third-Party Vendors',
                interests=['api_stability', 'sla_compliance', 'integration_support'],
                trust_level='partially_trusted',
                properties={
                    'types': ['payment_processors', 'credit_bureaus', 'cloud_providers']
                }
            )
        ]
        
        for stakeholder in stakeholders:
            self.session.add(stakeholder)
        
        # Adversaries
        adversaries = [
            Adversary(
                id='ADV-001',
                name='Organized Cybercrime Groups',
                type='organized_crime',
                technical_sophistication='high',
                resources='significant',
                capabilities={
                    'attack_vectors': ['phishing', 'malware', 'social_engineering', 'supply_chain'],
                    'tools': ['custom_malware', 'exploit_kits', 'botnets', 'ransomware'],
                    'persistence': 'high',
                    'stealth': 'advanced',
                    'attribution_difficulty': 'high'
                },
                primary_motivation='financial',
                objectives=['steal_credentials', 'ransomware_deployment', 'data_theft', 'fraud'],
                ttps={
                    'initial_access': ['spear_phishing', 'watering_hole', 'supply_chain_compromise'],
                    'execution': ['powershell', 'scheduled_tasks', 'wmi'],
                    'persistence': ['registry_keys', 'startup_folder', 'scheduled_tasks'],
                    'defense_evasion': ['obfuscation', 'process_injection', 'timestomping'],
                    'credential_access': ['keylogging', 'credential_dumping', 'brute_force'],
                    'lateral_movement': ['pass_the_hash', 'remote_desktop', 'smb'],
                    'exfiltration': ['https', 'dns_tunneling', 'cloud_storage']
                },
                known_campaigns=['carbanak', 'fin7', 'cobalt_group'],
                target_sectors=['financial_services', 'retail', 'hospitality']
            ),
            Adversary(
                id='ADV-002',
                name='Nation State Actors',
                type='nation_state',
                technical_sophistication='advanced',
                resources='unlimited',
                capabilities={
                    'attack_vectors': ['zero_day', 'supply_chain', 'physical_access', 'insider_threat'],
                    'tools': ['custom_implants', 'zero_days', 'hardware_implants'],
                    'persistence': 'extreme',
                    'stealth': 'extreme',
                    'attribution_difficulty': 'extreme'
                },
                primary_motivation='espionage',
                objectives=['intelligence_gathering', 'economic_espionage', 'disruption', 'preparation'],
                ttps={
                    'initial_access': ['supply_chain', 'zero_day', 'physical_access'],
                    'execution': ['custom_tools', 'living_off_land', 'firmware'],
                    'persistence': ['firmware_implants', 'kernel_rootkits', 'hardware'],
                    'defense_evasion': ['rootkits', 'anti_forensics', 'cover_channels'],
                    'collection': ['automated_collection', 'audio_capture', 'screen_capture'],
                    'command_control': ['custom_protocols', 'domain_fronting', 'dead_drops'],
                    'exfiltration': ['custom_protocols', 'physical_media', 'side_channels']
                },
                known_campaigns=['apt28', 'apt29', 'lazarus_group'],
                target_sectors=['financial_services', 'government', 'critical_infrastructure']
            ),
            Adversary(
                id='ADV-003',
                name='Malicious Insiders',
                type='insider',
                technical_sophistication='medium',
                resources='moderate',
                capabilities={
                    'attack_vectors': ['privileged_access_abuse', 'data_theft', 'sabotage'],
                    'tools': ['legitimate_tools', 'usb_devices', 'cloud_storage'],
                    'persistence': 'not_required',
                    'stealth': 'high',
                    'attribution_difficulty': 'low'
                },
                primary_motivation='financial',
                objectives=['data_theft', 'fraud', 'sabotage', 'espionage'],
                ttps={
                    'initial_access': ['valid_accounts'],
                    'execution': ['legitimate_tools', 'scripts'],
                    'persistence': ['valid_accounts'],
                    'defense_evasion': ['legitimate_credentials', 'timestomping'],
                    'collection': ['data_from_local_system', 'email_collection'],
                    'exfiltration': ['web_service', 'physical_media', 'email']
                },
                known_campaigns=['insider_fraud_cases'],
                target_sectors=['all_sectors']
            )
        ]
        
        for adversary in adversaries:
            self.session.add(adversary)
        
        self.session.flush()
    
    def _migrate_losses_and_hazards(self):
        """Create losses and hazards"""
        # Losses
        losses = [
            Loss(
                id='L-001',
                description='Customer financial loss due to unauthorized transactions',
                severity='critical',
                stakeholder_refs=['SH-001'],
                impact_type='financial',
                properties={
                    'max_impact': '$10M+',
                    'frequency': 'potential_daily',
                    'recovery_time': 'days_to_weeks'
                }
            ),
            Loss(
                id='L-002',
                description='Regulatory fines and penalties for compliance violations',
                severity='critical',
                stakeholder_refs=['SH-003'],
                impact_type='financial',
                properties={
                    'max_fine': '4% of global revenue or $20M',
                    'additional_impacts': ['license_suspension', 'increased_scrutiny']
                }
            ),
            Loss(
                id='L-003',
                description='Reputational damage leading to customer attrition',
                severity='high',
                stakeholder_refs=['SH-001'],
                impact_type='reputation',
                properties={
                    'customer_loss_rate': 'up to 30%',
                    'recovery_time': 'months_to_years',
                    'market_value_impact': 'significant'
                }
            ),
            Loss(
                id='L-004',
                description='Service unavailability preventing banking operations',
                severity='high',
                stakeholder_refs=['SH-001', 'SH-002'],
                impact_type='operational',
                properties={
                    'revenue_loss': '$1M per hour',
                    'sla_violation': 'yes',
                    'manual_processing_required': 'yes'
                }
            ),
            Loss(
                id='L-005',
                description='Customer PII exposure violating privacy regulations',
                severity='critical',
                stakeholder_refs=['SH-001', 'SH-003'],
                impact_type='privacy',
                properties={
                    'data_types': ['ssn', 'financial_records', 'personal_details'],
                    'gdpr_violation': 'yes',
                    'notification_required': '72_hours'
                }
            )
        ]
        
        for loss in losses:
            self.session.add(loss)
        
        # Hazards
        hazards = [
            Hazard(
                id='H-001',
                description='Unauthorized access to customer accounts',
                loss_refs=['L-001', 'L-003', 'L-005'],
                worst_case_scenario='Mass account compromise leading to widespread fraud and data breach',
                likelihood='likely',
                detection_difficulty='moderate',
                properties={
                    'attack_vectors': ['credential_theft', 'session_hijacking', 'account_takeover'],
                    'current_controls': ['mfa', 'fraud_detection', 'session_monitoring']
                }
            ),
            Hazard(
                id='H-002',
                description='System-wide service outage',
                loss_refs=['L-004'],
                worst_case_scenario='Complete banking platform unavailable for extended period',
                likelihood='possible',
                detection_difficulty='easy',
                properties={
                    'causes': ['ddos', 'infrastructure_failure', 'ransomware', 'misconfiguration'],
                    'mttr': '4_hours'
                }
            ),
            Hazard(
                id='H-003',
                description='Data integrity compromise in transaction processing',
                loss_refs=['L-001', 'L-002'],
                worst_case_scenario='Silent corruption of transaction data leading to incorrect balances',
                likelihood='unlikely',
                detection_difficulty='hard',
                properties={
                    'impact': 'financial_discrepancies',
                    'detection_lag': 'days_to_weeks'
                }
            ),
            Hazard(
                id='H-004',
                description='Large-scale customer data exfiltration',
                loss_refs=['L-002', 'L-003', 'L-005'],
                worst_case_scenario='Complete customer database stolen and sold on dark web',
                likelihood='possible',
                detection_difficulty='moderate',
                properties={
                    'data_volume': '1M+ records',
                    'regulatory_impact': 'severe',
                    'class_action_risk': 'high'
                }
            ),
            Hazard(
                id='H-005',
                description='AI-based fraud detection system manipulation',
                loss_refs=['L-001', 'L-003'],
                worst_case_scenario='Adversaries bypass fraud detection leading to massive losses',
                likelihood='possible',
                detection_difficulty='extreme',
                properties={
                    'attack_type': 'adversarial_ml',
                    'impact': 'undetected_fraud',
                    'ai_specific': 'yes'
                }
            )
        ]
        
        for hazard in hazards:
            self.session.add(hazard)
            self.hazard_map[hazard.id] = hazard
        
        self.session.flush()
    
    def _migrate_entities(self, entities_data: List[Dict[str, Any]]):
        """Migrate entities from demo data"""
        # Map demo entities to new schema
        entity_mappings = {
            'Web App': {
                'category': 'software',
                'subcategory': 'web_app',
                'technology': 'React 18',
                'criticality': 'critical',
                'trust_level': 'untrusted',
                'exposure': 'external'
            },
            'API Gateway': {
                'category': 'software',
                'subcategory': 'api_gateway',
                'technology': 'Kong Gateway',
                'criticality': 'critical',
                'trust_level': 'partially_trusted',
                'exposure': 'dmz'
            },
            'Auth Service': {
                'category': 'software',
                'subcategory': 'microservice',
                'technology': 'Node.js',
                'criticality': 'critical',
                'trust_level': 'trusted',
                'exposure': 'internal'
            },
            'Database': {
                'category': 'software',
                'subcategory': 'database',
                'technology': 'PostgreSQL 15',
                'criticality': 'critical',
                'trust_level': 'trusted',
                'exposure': 'internal'
            },
            'Fraud Detection AI': {
                'category': 'software',
                'subcategory': 'ai_system',
                'technology': 'TensorFlow',
                'criticality': 'high',
                'trust_level': 'trusted',
                'exposure': 'internal',
                'ai_properties': {
                    'ai_type': 'ml_model',
                    'model_details': {
                        'architecture': 'deep_neural_network',
                        'parameters': '10M',
                        'training_data': 'historical_transactions',
                        'update_frequency': 'weekly'
                    },
                    'capabilities': {
                        'real_time_scoring': True,
                        'pattern_recognition': True,
                        'anomaly_detection': True
                    },
                    'autonomy_level': 'supervised',
                    'decision_authority': ['flag_suspicious', 'risk_scoring'],
                    'trust_boundaries': {
                        'input_validation': 'required',
                        'output_verification': 'threshold_based'
                    }
                }
            }
        }
        
        for demo_entity in entities_data:
            name = demo_entity.get('name', '')
            mapping = entity_mappings.get(name, {})
            
            entity = Entity(
                id=demo_entity['id'],
                name=name,
                description=demo_entity.get('description', ''),
                category=mapping.get('category', 'software'),
                subcategory=mapping.get('subcategory'),
                technology=mapping.get('technology'),
                criticality=mapping.get('criticality', 'medium'),
                trust_level=mapping.get('trust_level', 'partially_trusted'),
                exposure=mapping.get('exposure', 'internal'),
                ai_properties=mapping.get('ai_properties'),
                properties={
                    'original_id': demo_entity['id'],
                    'position': demo_entity.get('position', {})
                }
            )
            
            self.session.add(entity)
            self.entity_map[demo_entity['id']] = entity
            
            # Create AI agent layers if applicable
            if entity.ai_properties:
                self._create_ai_layers(entity)
        
        # Create adversary control problems
        self._create_adversary_control_problems()
        
        self.session.flush()
    
    def _create_ai_layers(self, entity: Entity):
        """Create AI agent layers for AI entities"""
        if entity.name == 'Fraud Detection AI':
            layers = [
                AIAgentLayer(
                    agent_id=entity.id,
                    layer_type='perception',
                    vulnerabilities={
                        'data_poisoning': {
                            'severity': 'high',
                            'description': 'Training data contamination',
                            'mitigations': ['data_validation', 'anomaly_detection']
                        },
                        'feature_manipulation': {
                            'severity': 'medium',
                            'description': 'Adversarial feature engineering',
                            'mitigations': ['feature_monitoring', 'bounds_checking']
                        }
                    },
                    security_controls={
                        'input_validation': 'implemented',
                        'data_sanitization': 'implemented',
                        'rate_limiting': 'implemented'
                    }
                ),
                AIAgentLayer(
                    agent_id=entity.id,
                    layer_type='reasoning',
                    vulnerabilities={
                        'model_extraction': {
                            'severity': 'medium',
                            'description': 'Model behavior replication',
                            'mitigations': ['api_rate_limiting', 'output_perturbation']
                        },
                        'adversarial_examples': {
                            'severity': 'high',
                            'description': 'Crafted inputs causing misclassification',
                            'mitigations': ['adversarial_training', 'ensemble_models']
                        }
                    },
                    security_controls={
                        'model_versioning': 'implemented',
                        'performance_monitoring': 'implemented',
                        'drift_detection': 'planned'
                    }
                ),
                AIAgentLayer(
                    agent_id=entity.id,
                    layer_type='execution',
                    vulnerabilities={
                        'decision_manipulation': {
                            'severity': 'critical',
                            'description': 'Forcing incorrect fraud decisions',
                            'mitigations': ['human_review', 'confidence_thresholds']
                        }
                    },
                    security_controls={
                        'audit_logging': 'implemented',
                        'decision_explanation': 'implemented',
                        'override_capability': 'implemented'
                    }
                )
            ]
            
            for layer in layers:
                self.session.add(layer)
    
    def _create_adversary_control_problems(self):
        """Create adversary control problems for demo"""
        # Organized crime can influence external-facing components
        problems = [
            AdversaryControlProblem(
                adversary_id='ADV-001',
                entity_id=self.entity_map.get('1', Entity()).id if '1' in self.entity_map else None,  # Web App
                control_capability={
                    'can_observe': ['user_behavior', 'response_times', 'error_messages'],
                    'can_influence': ['input_data', 'request_timing'],
                    'can_disrupt': ['availability'],
                    'constraints': ['external_only', 'no_direct_backend_access']
                }
            ),
            AdversaryControlProblem(
                adversary_id='ADV-003',
                entity_id=self.entity_map.get('3', Entity()).id if '3' in self.entity_map else None,  # Auth Service
                control_capability={
                    'can_observe': ['all_authentication_data', 'user_sessions'],
                    'can_influence': ['authentication_decisions', 'session_management'],
                    'can_disrupt': ['authentication_flow', 'data_integrity'],
                    'constraints': ['detection_risk', 'audit_trails']
                }
            )
        ]
        
        for problem in problems:
            if problem.entity_id:  # Only add if entity exists
                self.session.add(problem)
    
    def _migrate_relationships(self, relationships_data: List[Dict[str, Any]]):
        """Migrate relationships with enhanced properties"""
        # Create a main control loop
        main_loop = ControlLoop(
            id='CL-001',
            name='Transaction Processing Loop',
            purpose='Process and validate banking transactions',
            controlled_process='transaction_flow',
            control_algorithm='Sequential validation with fraud detection',
            process_model={
                'assumed_state': {
                    'user_authenticated': True,
                    'account_active': True,
                    'sufficient_balance': True
                },
                'state_update_sources': ['auth_service', 'account_service', 'transaction_service'],
                'update_frequency': 'event_driven',
                'staleness_tolerance': '1_minute'
            },
            loop_frequency='continuous',
            max_loop_delay='5s'
        )
        self.session.add(main_loop)
        
        # Migrate relationships
        for rel_data in relationships_data:
            source_id = rel_data.get('source')
            target_id = rel_data.get('target')
            
            # Skip if entities don't exist
            if source_id not in self.entity_map or target_id not in self.entity_map:
                continue
            
            # Determine properties based on relationship
            props = self._determine_relationship_properties(
                self.entity_map[source_id],
                self.entity_map[target_id],
                rel_data.get('label', '')
            )
            
            relationship = Relationship(
                id=rel_data.get('id', f"R-{source_id}-{target_id}"),
                source_id=self.entity_map[source_id].id,
                target_id=self.entity_map[target_id].id,
                action=rel_data.get('label', 'Unknown Action'),
                type=props['type'],
                control_loop_id=main_loop.id if props['in_main_loop'] else None,
                protocol=props['protocol'],
                encryption=props['encryption'],
                authentication=props['authentication'],
                data_sensitivity=props['data_sensitivity'],
                timing_type=props['timing_type'],
                properties={
                    'original_id': rel_data.get('id'),
                    'migrated_from_demo': True
                }
            )
            
            self.session.add(relationship)
            self.relationship_map[rel_data.get('id')] = relationship
        
        self.session.flush()
    
    def _determine_relationship_properties(self, source: Entity, target: Entity, label: str) -> Dict[str, Any]:
        """Determine relationship properties based on entities and label"""
        props = {
            'type': 'control',
            'protocol': 'HTTPS',
            'encryption': 'TLS1.3',
            'authentication': 'oauth2',
            'data_sensitivity': 'confidential',
            'timing_type': 'synchronous',
            'in_main_loop': True
        }
        
        # Customize based on relationship type
        if 'response' in label.lower() or 'return' in label.lower():
            props['type'] = 'feedback'
        
        if source.exposure == 'external' or target.exposure == 'external':
            props['authentication'] = 'mutual_tls'
            props['data_sensitivity'] = 'secret'
        
        if 'database' in target.name.lower():
            props['protocol'] = 'PostgreSQL'
            props['timing_type'] = 'synchronous'
        
        if 'ai' in source.name.lower() or 'ai' in target.name.lower():
            props['data_sensitivity'] = 'secret'
            props['in_main_loop'] = False  # AI operates asynchronously
            props['timing_type'] = 'asynchronous'
        
        return props
    
    def _migrate_analyses(self, analyses_data: Dict[str, Any]):
        """Migrate analysis results to new schema"""
        # This would parse the existing analysis data and create Analysis records
        # For demo purposes, we'll create some sample analyses
        
        for rel_id, relationship in self.relationship_map.items():
            # Create STPA-Sec analysis
            analysis = Analysis(
                id=f"A-{rel_id}",
                relationship_id=relationship.id,
                analysis_type='stpa-sec',
                uca_not_provided={
                    'exists': True,
                    'description': f"{relationship.action} not provided when required",
                    'context': 'Service unavailable or network failure',
                    'severity': 'high',
                    'hazard_refs': ['H-002', 'H-004']
                },
                uca_provided_causes_hazard={
                    'exists': True,
                    'description': f"{relationship.action} sent with malicious intent",
                    'context': 'Compromised source or MITM attack',
                    'severity': 'critical',
                    'hazard_refs': ['H-001', 'H-003']
                },
                stride_spoofing={
                    'exists': True,
                    'description': 'Identity spoofing possible',
                    'attack_vector': 'Token theft or replay',
                    'severity': 'high',
                    'hazard_refs': ['H-001']
                },
                analyzed_by='demo_migration',
                confidence_score=0.85
            )
            
            self.session.add(analysis)
            self.analysis_map[analysis.id] = analysis
        
        self.session.flush()
    
    def _migrate_scenarios(self, scenarios_data: Any):
        """Create scenarios based on analyses"""
        # Create high-risk scenarios
        scenarios = [
            Scenario(
                id='SC-001',
                relationship_id=list(self.relationship_map.values())[0].id if self.relationship_map else None,
                description='Credential stuffing attack bypasses authentication',
                uca_refs=['not_provided'],
                stride_refs=['spoofing'],
                hazard_refs=['H-001'],
                threat_actor_refs=['ADV-001'],
                attack_chain=[
                    'Obtain credentials from data breach',
                    'Automate login attempts',
                    'Bypass rate limiting',
                    'Access customer accounts'
                ],
                prerequisites=['Valid credentials', 'Automated tools'],
                likelihood='likely',
                impact='major',
                d4_assessment={
                    'detectability': {'score': 3, 'rationale': 'Patterns visible in logs'},
                    'difficulty': {'score': 2, 'rationale': 'Tools readily available'},
                    'damage': {'score': 4, 'rationale': 'Direct financial loss'},
                    'deniability': {'score': 4, 'rationale': 'Hard to attribute'},
                    'overall_score': 13,
                    'priority': 'high'
                }
            ),
            Scenario(
                id='SC-002',
                description='AI fraud detection poisoning attack',
                hazard_refs=['H-005'],
                threat_actor_refs=['ADV-001', 'ADV-002'],
                attack_chain=[
                    'Study fraud detection patterns',
                    'Create synthetic normal transactions',
                    'Gradually poison training data',
                    'Cause model to misclassify fraud'
                ],
                prerequisites=['Understanding of ML system', 'Patience'],
                likelihood='possible',
                impact='catastrophic',
                d4_assessment={
                    'detectability': {'score': 5, 'rationale': 'Extremely hard to detect'},
                    'difficulty': {'score': 4, 'rationale': 'Requires expertise'},
                    'damage': {'score': 5, 'rationale': 'Massive fraud losses'},
                    'deniability': {'score': 5, 'rationale': 'Nearly impossible to prove'},
                    'overall_score': 19,
                    'priority': 'critical'
                }
            )
        ]
        
        for scenario in scenarios:
            if scenario.relationship_id or not scenario.relationship_id:  # Allow scenarios without relationships
                self.session.add(scenario)
        
        # Create sample mitigations
        mitigations = [
            Mitigation(
                id='M-001',
                name='Implement Adaptive MFA',
                description='Risk-based multi-factor authentication',
                type='preventive',
                category='technical',
                effectiveness='high',
                implementation_difficulty='moderate',
                cost_estimate={
                    'initial': {'amount': 250000, 'currency': 'USD'},
                    'recurring': {'amount': 50000, 'currency': 'USD', 'period': 'annual'}
                },
                implementation_steps=[
                    'Select MFA solution',
                    'Integrate with auth service',
                    'Configure risk rules',
                    'User enrollment campaign',
                    'Monitor and tune'
                ]
            ),
            Mitigation(
                id='M-002',
                name='AI Model Hardening',
                description='Implement adversarial training and monitoring',
                type='preventive',
                category='technical',
                effectiveness='high',
                implementation_difficulty='hard',
                cost_estimate={
                    'initial': {'amount': 500000, 'currency': 'USD'},
                    'recurring': {'amount': 100000, 'currency': 'USD', 'period': 'annual'}
                },
                implementation_steps=[
                    'Implement adversarial training',
                    'Add input validation',
                    'Deploy model monitoring',
                    'Create feedback loops',
                    'Regular model updates'
                ]
            )
        ]
        
        for mitigation in mitigations:
            self.session.add(mitigation)
        
        self.session.flush()

def migrate_demo_data(session: Session, demo_data_path: str = None) -> Dict[str, Any]:
    """Main function to migrate demo data"""
    migrator = DemoDataMigrator(session)
    
    # For now, use hardcoded demo data structure
    # In production, this would load from demo_data_path
    demo_data = {
        'entities': [
            {'id': '1', 'name': 'Web App', 'type': 'component'},
            {'id': '2', 'name': 'API Gateway', 'type': 'component'},
            {'id': '3', 'name': 'Auth Service', 'type': 'component'},
            {'id': '4', 'name': 'Database', 'type': 'component'},
            {'id': '5', 'name': 'Fraud Detection AI', 'type': 'component'}
        ],
        'relationships': [
            {'id': 'r1', 'source': '1', 'target': '2', 'label': 'API Request'},
            {'id': 'r2', 'source': '2', 'target': '3', 'label': 'Validate Token'},
            {'id': 'r3', 'source': '3', 'target': '4', 'label': 'Check Credentials'},
            {'id': 'r4', 'source': '4', 'target': '3', 'label': 'Return User Data'},
            {'id': 'r5', 'source': '3', 'target': '2', 'label': 'Auth Response'},
            {'id': 'r6', 'source': '2', 'target': '5', 'label': 'Check Transaction'},
            {'id': 'r7', 'source': '5', 'target': '2', 'label': 'Risk Score'}
        ]
    }
    
    return migrator.migrate_all(demo_data)