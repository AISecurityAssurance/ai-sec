#!/usr/bin/env python3
"""
Populate database with comprehensive STPA-Sec demo data for the banking application
"""
import json
from datetime import datetime
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings
from src.database.stpa_sec_models import (
    Base, SystemDefinition, Stakeholder, Adversary, Loss, Hazard,
    Entity, Relationship, Analysis, Scenario, Mitigation, ScenarioMitigation
)


def clear_existing_data(session):
    """Clear any existing data to avoid conflicts"""
    print("Clearing existing data...")
    session.query(ScenarioMitigation).delete()
    session.query(Mitigation).delete()
    session.query(Scenario).delete()
    session.query(Analysis).delete()  # This is stpa_analyses table
    session.query(Relationship).delete()
    session.query(Entity).delete()
    session.query(Hazard).delete()
    session.query(Loss).delete()
    session.query(Adversary).delete()
    session.query(Stakeholder).delete()
    session.query(SystemDefinition).delete()
    session.commit()
    print("✓ Data cleared")


def populate_demo_data(session):
    """Populate comprehensive demo data for banking application"""
    
    # 1. System Definition
    print("\n1. Creating system definition...")
    system_def = SystemDefinition(
        id='banking-system-001',
        mission_statement={
            "primary_mission": "Provide secure, reliable, and compliant digital banking services to retail and business customers",
            "description": "Digital banking platform supporting web and mobile channels for account management, payments, and financial services",
            "domain": "financial_services",
            "purpose": "Enable customers to securely manage their finances while protecting against cyber threats and ensuring regulatory compliance"
        },
        system_boundaries={
            "in_scope": [
                "Web banking application",
                "Mobile banking apps (iOS/Android)",
                "API Gateway and microservices",
                "Authentication and authorization services",
                "Core banking integration layer",
                "Fraud detection AI system",
                "Customer data storage"
            ],
            "out_scope": [
                "ATM network",
                "Physical branch systems",
                "Core banking mainframe",
                "Third-party payment processors (external APIs only)"
            ],
            "assumptions": [
                "Users access the system via untrusted networks",
                "Mobile devices may be compromised",
                "Insider threats are possible",
                "Nation-state actors may target the system"
            ]
        },
        operational_context={
            "environment": {
                "deployment": "Hybrid cloud (AWS + on-premise)",
                "users": "5M+ retail customers, 50K business customers",
                "transactions": "10M+ transactions/day",
                "availability": "99.99% SLA"
            },
            "constraints": [
                "PCI-DSS compliance required",
                "GDPR/CCPA privacy regulations",
                "Real-time transaction processing",
                "Legacy system integration requirements"
            ],
            "dependencies": [
                "AWS cloud services",
                "Third-party identity verification",
                "SMS/Email gateways",
                "Credit bureau APIs"
            ]
        }
    )
    session.add(system_def)
    
    # 2. Stakeholders
    print("2. Creating stakeholders...")
    stakeholders = [
        Stakeholder(
            id='stake-customers',
            name='Retail Banking Customers',
            type='primary',
            interests=['Account security', 'Service availability', 'Privacy protection', 'Easy access'],
            trust_level='trusted',
            properties={
                "count": "5M+",
                "concerns": ["Identity theft", "Financial loss", "Privacy breach"],
                "expectations": ["24/7 availability", "Mobile access", "Quick transactions"]
            }
        ),
        Stakeholder(
            id='stake-business',
            name='Business Banking Customers',
            type='primary',
            interests=['Bulk transactions', 'API access', 'Fraud prevention', 'Compliance'],
            trust_level='trusted',
            properties={
                "count": "50K+",
                "concerns": ["Business continuity", "Transaction limits", "Integration capabilities"],
                "expectations": ["API reliability", "Batch processing", "Detailed reporting"]
            }
        ),
        Stakeholder(
            id='stake-regulators',
            name='Financial Regulators',
            type='secondary',
            interests=['Compliance', 'Consumer protection', 'System stability', 'Anti-money laundering'],
            trust_level='trusted',
            properties={
                "entities": ["FDIC", "OCC", "CFPB", "FinCEN"],
                "requirements": ["Regular audits", "Incident reporting", "Compliance documentation"]
            }
        ),
        Stakeholder(
            id='stake-employees',
            name='Bank Employees',
            type='secondary',
            interests=['System usability', 'Customer support tools', 'Security training'],
            trust_level='partially_trusted',
            properties={
                "roles": ["Customer service", "IT operations", "Security team", "Executives"],
                "access_levels": ["Read-only", "Transaction approval", "Administrative"]
            }
        )
    ]
    session.add_all(stakeholders)
    
    # 3. Adversaries
    print("3. Creating adversaries...")
    adversaries = [
        Adversary(
            id='adv-cybercrime',
            name='Organized Cybercrime Group',
            type='organized_crime',
            technical_sophistication='high',
            resources='significant',
            primary_motivation='financial',
            objectives=['Steal customer funds', 'Sell customer data', 'Ransomware attacks'],
            capabilities={
                "technical": ["Zero-day exploits", "Advanced malware", "Social engineering"],
                "operational": ["24/7 operations", "Multiple attack vectors", "Money laundering"]
            },
            ttps={
                "tactics": ["Initial Access", "Persistence", "Privilege Escalation", "Exfiltration"],
                "techniques": ["Phishing", "Supply chain compromise", "Credential stuffing"],
                "procedures": ["Automated attacks", "Manual exploitation", "Living off the land"]
            }
        ),
        Adversary(
            id='adv-nation-state',
            name='Nation State APT',
            type='nation_state',
            technical_sophistication='advanced',
            resources='unlimited',
            primary_motivation='espionage',
            objectives=['Economic espionage', 'Disrupt financial system', 'Gather intelligence'],
            capabilities={
                "technical": ["Custom implants", "Zero-days", "Supply chain attacks", "AI-powered attacks"],
                "operational": ["Long-term persistence", "Multiple teams", "Government backing"]
            },
            ttps={
                "tactics": ["Reconnaissance", "Resource Development", "Initial Access", "Persistence"],
                "techniques": ["Spear phishing", "Watering hole", "Hardware implants"],
                "procedures": ["Slow and deliberate", "Anti-forensics", "False flags"]
            }
        ),
        Adversary(
            id='adv-insider',
            name='Malicious Insider',
            type='insider',
            technical_sophistication='medium',
            resources='minimal',
            primary_motivation='financial',
            objectives=['Steal customer data', 'Commit fraud', 'Sell access'],
            capabilities={
                "technical": ["Legitimate access", "Knowledge of systems", "Bypass controls"],
                "operational": ["Physical access", "Social engineering", "Process knowledge"]
            },
            ttps={
                "tactics": ["Privilege Abuse", "Data Theft", "Covering Tracks"],
                "techniques": ["Database dumps", "Screenshot capture", "Log deletion"],
                "procedures": ["Gradual escalation", "Small transactions", "Collusion"]
            }
        )
    ]
    session.add_all(adversaries)
    
    # 4. Losses
    print("4. Creating losses...")
    losses = [
        Loss(
            id='L-1',
            description='Customer financial loss due to unauthorized transactions',
            severity='critical',
            impact_type='financial',
            stakeholder_refs=['stake-customers', 'stake-business'],
            properties={
                "metrics": {"max_loss": "$10M+", "frequency": "High impact if occurs"},
                "impact_areas": ["Customer trust", "Regulatory fines", "Legal liability"]
            }
        ),
        Loss(
            id='L-2',
            description='Regulatory non-compliance resulting in fines and sanctions',
            severity='critical',
            impact_type='financial',
            stakeholder_refs=['stake-regulators'],
            properties={
                "metrics": {"potential_fines": "$100M+", "license_risk": "Operating license suspension"},
                "impact_areas": ["Business operations", "Market access", "Reputation"]
            }
        ),
        Loss(
            id='L-3',
            description='Customer PII exposure leading to identity theft',
            severity='high',
            impact_type='privacy',
            stakeholder_refs=['stake-customers'],
            properties={
                "metrics": {"affected_users": "Potentially millions", "notification_cost": "$100/user"},
                "impact_areas": ["Privacy violations", "GDPR fines", "Class action lawsuits"]
            }
        ),
        Loss(
            id='L-4',
            description='Service outage preventing customer access to funds',
            severity='high',
            impact_type='operational',
            stakeholder_refs=['stake-customers', 'stake-business'],
            properties={
                "metrics": {"downtime_cost": "$1M/hour", "SLA_penalties": "Significant"},
                "impact_areas": ["Customer satisfaction", "Revenue loss", "Competitive disadvantage"]
            }
        ),
        Loss(
            id='L-5',
            description='Reputational damage leading to customer attrition',
            severity='high',
            impact_type='reputation',
            stakeholder_refs=['stake-customers', 'stake-business'],
            properties={
                "metrics": {"customer_churn": "10-20% potential", "market_cap_impact": "$1B+"},
                "impact_areas": ["Brand value", "Customer acquisition cost", "Partner relationships"]
            }
        )
    ]
    session.add_all(losses)
    
    # 5. Hazards
    print("5. Creating hazards...")
    hazards = [
        Hazard(
            id='H-1',
            description='Authentication system accepts invalid credentials allowing unauthorized account access',
            loss_refs=['L-1', 'L-3'],
            properties={
                "system_state": "Authentication service in compromised state accepting any password",
                "environmental_conditions": ["High login volume", "Degraded performance"],
                "triggers": ["Authentication bypass vulnerability", "Credential stuffing attack"]
            }
        ),
        Hazard(
            id='H-2',
            description='Transaction authorization system fails to verify transaction legitimacy',
            loss_refs=['L-1', 'L-2'],
            properties={
                "system_state": "Authorization rules bypassed or disabled",
                "environmental_conditions": ["Peak transaction periods", "System maintenance"],
                "triggers": ["Logic flaw exploitation", "Session hijacking"]
            }
        ),
        Hazard(
            id='H-3',
            description='Database encryption keys exposed allowing mass data decryption',
            loss_refs=['L-3', 'L-2', 'L-5'],
            properties={
                "system_state": "Encryption keys accessible to unauthorized parties",
                "environmental_conditions": ["Key rotation in progress", "Backup restoration"],
                "triggers": ["Insider threat", "Cloud misconfiguration", "Supply chain compromise"]
            }
        ),
        Hazard(
            id='H-4',
            description='Critical services unavailable preventing customer transactions',
            loss_refs=['L-4', 'L-5'],
            properties={
                "system_state": "Core services offline or unresponsive",
                "environmental_conditions": ["High load", "Infrastructure failure"],
                "triggers": ["DDoS attack", "Ransomware", "Cascading failure"]
            }
        ),
        Hazard(
            id='H-5',
            description='AI fraud detection system poisoned to allow malicious transactions',
            loss_refs=['L-1', 'L-2'],
            properties={
                "system_state": "ML model compromised and making incorrect decisions",
                "environmental_conditions": ["Model retraining", "New attack patterns"],
                "triggers": ["Data poisoning", "Adversarial inputs", "Model inversion"]
            }
        )
    ]
    session.add_all(hazards)
    
    # 6. Entities
    print("6. Creating entities...")
    entities = [
        Entity(
            id='ent-web-app',
            name='Web Banking Application',
            category='software',
            description='Customer-facing web application for banking services',
            criticality='critical',
            trust_level='trusted',
            exposure='public',
            properties={
                "type": "controller",
                "technology": "React 18 + TypeScript",
                "version": "v2.5.0",
                "responsibilities": [
                    "User interface rendering",
                    "Input validation",
                    "Session management",
                    "API communication"
                ],
                "process_model": {
                    "user_session": "JWT tokens",
                    "state_management": "Redux",
                    "security_headers": "CSP, HSTS, X-Frame-Options"
                }
            }
        ),
        Entity(
            id='ent-mobile-app',
            name='Mobile Banking App',
            category='software',
            description='Native mobile applications for iOS and Android',
            criticality='critical',
            trust_level='partially_trusted',
            exposure='public',
            properties={
                "type": "controller",
                "technology": "React Native",
                "version": "v3.1.0",
                "responsibilities": [
                    "Biometric authentication",
                    "Secure storage",
                    "Push notifications",
                    "Camera access for check deposit"
                ],
                "process_model": {
                    "auth_method": "Biometric + PIN",
                    "storage": "Encrypted keychain/keystore",
                    "certificate_pinning": "Enabled"
                }
            }
        ),
        Entity(
            id='ent-api-gateway',
            name='API Gateway',
            category='software',
            description='Central API gateway for all client requests',
            criticality='critical',
            trust_level='trusted',
            exposure='dmz',
            properties={
                "type": "controller",
                "technology": "Kong Gateway",
                "version": "v3.0",
                "responsibilities": [
                    "Request routing",
                    "Rate limiting",
                    "Authentication verification",
                    "Request/response transformation",
                    "API versioning"
                ],
                "process_model": {
                    "rate_limits": "1000 req/min per user",
                    "auth_plugins": "OAuth2, JWT validation",
                    "monitoring": "Prometheus metrics"
                }
            }
        ),
        Entity(
            id='ent-auth-service',
            name='Authentication Service',
            category='software',
            description='Centralized authentication and authorization service',
            criticality='critical',
            trust_level='critical',
            exposure='internal',
            properties={
                "type": "controller",
                "technology": "Node.js + Passport",
                "version": "v1.8.0",
                "responsibilities": [
                    "User authentication",
                    "MFA coordination",
                    "Session management",
                    "Token generation",
                    "Password policy enforcement"
                ],
                "process_model": {
                    "auth_flows": "OAuth2, SAML, OpenID Connect",
                    "mfa_methods": "SMS, TOTP, Push notification",
                    "password_policy": "12+ chars, complexity requirements"
                }
            }
        ),
        Entity(
            id='ent-fraud-ai',
            name='Fraud Detection AI',
            category='software',
            description='Machine learning system for fraud detection',
            criticality='high',
            trust_level='trusted',
            exposure='internal',
            ai_properties={
                "model_type": "Ensemble (Random Forest + Neural Network)",
                "training_frequency": "Daily incremental, weekly full",
                "feature_count": 150,
                "accuracy_metrics": {
                    "precision": 0.95,
                    "recall": 0.88,
                    "f1_score": 0.91
                }
            },
            properties={
                "type": "controller",
                "technology": "Python + TensorFlow",
                "version": "v2.0.0",
                "responsibilities": [
                    "Real-time transaction scoring",
                    "Pattern recognition",
                    "Anomaly detection",
                    "Risk assessment",
                    "Alert generation"
                ],
                "process_model": {
                    "decision_threshold": 0.85,
                    "feature_pipeline": "Real-time + historical",
                    "explainability": "SHAP values provided"
                }
            }
        ),
        Entity(
            id='ent-database',
            name='Customer Database',
            category='software',
            description='Primary database for customer data and transactions',
            criticality='critical',
            trust_level='critical',
            exposure='internal',
            properties={
                "type": "controlled_process",
                "technology": "PostgreSQL 15",
                "deployment": "AWS RDS Multi-AZ",
                "responsibilities": [
                    "Data persistence",
                    "Transaction integrity",
                    "Encryption at rest",
                    "Audit logging",
                    "Backup management"
                ],
                "process_model": {
                    "encryption": "AES-256 at rest",
                    "backup_schedule": "Hourly snapshots, daily full",
                    "retention": "90 days online, 7 years archive"
                }
            }
        )
    ]
    session.add_all(entities)
    
    # 7. Relationships
    print("7. Creating relationships...")
    relationships = [
        Relationship(
            id='rel-web-to-api',
            source_id='ent-web-app',
            target_id='ent-api-gateway',
            action='Submit API request',
            type='control',
            protocol='HTTPS/REST',
            data_sensitivity='confidential',
            properties={
                "description": "Web app sends user requests to API gateway",
                "control_actions": ["Login request", "View accounts", "Transfer money", "Pay bills"],
                "feedback_info": ["API responses", "Error messages", "Rate limit status"],
                "data_format": {"request": "JSON", "response": "JSON"},
                "timing_constraints": ["Response within 2 seconds", "Timeout after 30 seconds"]
            }
        ),
        Relationship(
            id='rel-mobile-to-api',
            source_id='ent-mobile-app',
            target_id='ent-api-gateway',
            action='Submit mobile API request',
            type='control',
            protocol='HTTPS/REST',
            data_sensitivity='confidential',
            properties={
                "description": "Mobile app sends user requests to API gateway",
                "control_actions": ["Biometric login", "Check deposit", "Quick balance", "Find ATM"],
                "feedback_info": ["API responses", "Push notifications", "Sync status"],
                "certificate_pinning": True,
                "additional_headers": ["X-Device-ID", "X-App-Version"]
            }
        ),
        Relationship(
            id='rel-api-to-auth',
            source_id='ent-api-gateway',
            target_id='ent-auth-service',
            action='Validate authentication',
            type='control',
            protocol='gRPC',
            data_sensitivity='secret',
            properties={
                "description": "API gateway validates tokens with auth service",
                "control_actions": ["Verify token", "Check permissions", "Refresh token", "Revoke token"],
                "feedback_info": ["Token valid/invalid", "User permissions", "Token metadata"],
                "performance": "Sub-100ms response required",
                "caching": "5-minute cache for valid tokens"
            }
        ),
        Relationship(
            id='rel-api-to-fraud',
            source_id='ent-api-gateway',
            target_id='ent-fraud-ai',
            action='Check transaction risk',
            type='control',
            protocol='HTTP/REST',
            data_sensitivity='confidential',
            properties={
                "description": "API gateway sends transactions for fraud scoring",
                "control_actions": ["Score transaction", "Check velocity", "Verify patterns"],
                "feedback_info": ["Risk score", "Fraud indicators", "Recommended action"],
                "async_mode": "Fire-and-forget for low-value transactions"
            }
        ),
        Relationship(
            id='rel-auth-to-db',
            source_id='ent-auth-service',
            target_id='ent-database',
            action='Query user credentials',
            type='control',
            protocol='PostgreSQL wire protocol',
            data_sensitivity='secret',
            properties={
                "description": "Auth service queries user data from database",
                "control_actions": ["Fetch user", "Update last login", "Check MFA status", "Log attempts"],
                "feedback_info": ["User records", "Query results", "Transaction status"],
                "connection_pool": "Min 10, Max 100 connections",
                "encryption": "TLS 1.3 required"
            }
        ),
        Relationship(
            id='rel-fraud-to-db',
            source_id='ent-fraud-ai',
            target_id='ent-database',
            action='Query transaction history',
            type='control',
            protocol='PostgreSQL wire protocol',
            data_sensitivity='confidential',
            properties={
                "description": "Fraud AI queries historical data for analysis",
                "control_actions": ["Fetch transactions", "Get user patterns", "Store scores", "Update models"],
                "feedback_info": ["Historical data", "Aggregated stats", "Write confirmation"],
                "read_replica": True,
                "batch_mode": "Supported for training"
            }
        )
    ]
    session.add_all(relationships)
    
    # 8. Analyses (UCAs)
    print("8. Creating analyses...")
    analyses = [
        Analysis(
            id='ana-web-api-auth',
            relationship_id='rel-web-to-api',
            analysis_type='stpa-sec',
            uca_not_provided={
                "description": "Web app fails to include authentication token",
                "hazard_refs": ["H-1"],
                "conditions": ["Token expired", "Session timeout", "Client-side error"],
                "adversarial_action": "Attacker exploits missing auth to access APIs"
            },
            uca_provided_causes_hazard={
                "description": "Web app sends malformed authentication causing bypass",
                "hazard_refs": ["H-1", "H-2"],
                "conditions": ["XSS attack", "Token manipulation", "Replay attack"],
                "adversarial_action": "Attacker injects malicious auth tokens"
            },
            uca_wrong_timing={
                "description": "Authentication sent after sensitive action",
                "hazard_refs": ["H-2"],
                "conditions": ["Race condition", "Async timing issue"],
                "adversarial_action": "Attacker exploits timing window"
            },
            analyzed_by='stpa-sec-agent',
            confidence_score=0.92
        ),
        Analysis(
            id='ana-api-fraud-check',
            relationship_id='rel-api-to-fraud',
            analysis_type='stpa-sec',
            uca_not_provided={
                "description": "API gateway skips fraud check for transactions",
                "hazard_refs": ["H-2", "H-5"],
                "conditions": ["Fraud service down", "Timeout", "Configuration error"],
                "adversarial_action": "Attacker times requests during outage"
            },
            uca_provided_causes_hazard={
                "description": "API sends poisoned data to fraud AI",
                "hazard_refs": ["H-5"],
                "conditions": ["Input validation bypass", "API compromise"],
                "adversarial_action": "Attacker poisons ML model via crafted inputs"
            },
            analyzed_by='stpa-sec-agent',
            confidence_score=0.88
        )
    ]
    session.add_all(analyses)
    
    # 9. Scenarios
    print("9. Creating scenarios...")
    scenarios = [
        Scenario(
            id='scn-account-takeover',
            relationship_id='rel-web-to-api',
            hazard_refs=['H-1', 'H-2'],
            description='Sophisticated account takeover via authentication bypass',
            attack_chain=[
                "Reconnaissance: Gather target user information",
                "Initial Access: Phishing email with credential stealer",
                "Exploitation: Use stolen creds with session replay",
                "Persistence: Install web shell for continued access",
                "Action: Transfer funds to mule accounts"
            ],
            prerequisites=[
                "Valid user email addresses",
                "Phishing infrastructure",
                "Money mule network",
                "Session replay tools"
            ],
            likelihood='likely',
            impact='major',
            contributing_factors={
                "technical": ["Weak session validation", "No device fingerprinting"],
                "procedural": ["Insufficient security awareness training"],
                "environmental": ["Work-from-home increasing phishing success"]
            }
        ),
        Scenario(
            id='scn-ai-poisoning',
            relationship_id='rel-api-to-fraud',
            hazard_refs=['H-5'],
            description='Long-term fraud AI poisoning campaign',
            attack_chain=[
                "Preparation: Create synthetic identities",
                "Seeding: Establish 'normal' behavior patterns",
                "Poisoning: Gradually introduce malicious patterns",
                "Exploitation: Execute fraud while AI allows it",
                "Cashout: Quick extraction before detection"
            ],
            prerequisites=[
                "Multiple synthetic identities",
                "Understanding of AI model features",
                "Patient, long-term operation",
                "Cryptocurrency cashout infrastructure"
            ],
            likelihood='possible',
            impact='catastrophic',
            contributing_factors={
                "technical": ["Lack of adversarial training", "No data validation"],
                "procedural": ["Infrequent model audits"],
                "environmental": ["Increasing AI adoption without security"]
            }
        )
    ]
    session.add_all(scenarios)
    
    # 10. Mitigations
    print("10. Creating mitigations...")
    mitigations = [
        Mitigation(
            id='mit-adaptive-mfa',
            name='Adaptive Multi-Factor Authentication',
            description='Risk-based MFA that adjusts requirements based on context',
            type='preventive',
            category='technical',
            effectiveness='high',
            implementation_difficulty='moderate',
            cost_estimate={
                "initial": "$500K",
                "annual": "$100K",
                "timeline": "6 months"
            },
            implementation_steps=[
                "Select adaptive MFA solution",
                "Integrate with authentication service",
                "Define risk scoring rules",
                "Implement step-up authentication",
                "User enrollment campaign"
            ],
            requirements=[
                "MFA infrastructure",
                "Risk scoring engine",
                "User device management",
                "SMS/Push notification capability"
            ]
        ),
        Mitigation(
            id='mit-ai-hardening',
            name='AI Model Security Hardening',
            description='Comprehensive security measures for fraud detection AI',
            type='preventive',
            category='technical',
            effectiveness='high',
            implementation_difficulty='hard',
            cost_estimate={
                "initial": "$1M",
                "annual": "$200K",
                "timeline": "12 months"
            },
            implementation_steps=[
                "Implement adversarial training",
                "Add input validation layer",
                "Deploy model monitoring",
                "Create rollback capability",
                "Establish model security testing"
            ],
            requirements=[
                "ML security expertise",
                "Additional compute resources",
                "Model versioning system",
                "Security testing framework"
            ]
        ),
        Mitigation(
            id='mit-zero-trust',
            name='Zero Trust Architecture',
            description='Implement zero trust principles across all systems',
            type='preventive',
            category='technical',
            effectiveness='very_high',
            implementation_difficulty='extreme',
            cost_estimate={
                "initial": "$5M",
                "annual": "$500K",
                "timeline": "24 months"
            },
            implementation_steps=[
                "Network microsegmentation",
                "Identity-based access control",
                "Continuous verification",
                "Least privilege enforcement",
                "Encrypted communications everywhere"
            ],
            requirements=[
                "Complete network redesign",
                "New identity platform",
                "Policy engine",
                "Extensive testing"
            ]
        )
    ]
    session.add_all(mitigations)
    
    # 11. Link scenarios to mitigations
    print("11. Linking scenarios to mitigations...")
    scenario_mitigations = [
        ScenarioMitigation(
            scenario_id='scn-account-takeover',
            mitigation_id='mit-adaptive-mfa',
            effectiveness_for_scenario='substantial',
            implementation_priority=9,
            notes='Would prevent most account takeover attempts by requiring additional verification'
        ),
        ScenarioMitigation(
            scenario_id='scn-account-takeover',
            mitigation_id='mit-zero-trust',
            effectiveness_for_scenario='complete',
            implementation_priority=7,
            notes='Would prevent lateral movement even after initial compromise'
        ),
        ScenarioMitigation(
            scenario_id='scn-ai-poisoning',
            mitigation_id='mit-ai-hardening',
            effectiveness_for_scenario='substantial',
            implementation_priority=8,
            notes='Would detect and prevent most poisoning attempts'
        )
    ]
    session.add_all(scenario_mitigations)
    
    # Commit all data
    session.commit()
    print("\n✓ All demo data populated successfully!")
    
    # Print summary
    print("\nDemo Data Summary:")
    print(f"  - System Definitions: 1")
    print(f"  - Stakeholders: {len(stakeholders)}")
    print(f"  - Adversaries: {len(adversaries)}")
    print(f"  - Losses: {len(losses)}")
    print(f"  - Hazards: {len(hazards)}")
    print(f"  - Entities: {len(entities)}")
    print(f"  - Relationships: {len(relationships)}")
    print(f"  - Analyses: {len(analyses)}")
    print(f"  - Scenarios: {len(scenarios)}")
    print(f"  - Mitigations: {len(mitigations)}")
    print(f"  - Scenario-Mitigation Links: {len(scenario_mitigations)}")


def main():
    """Main function"""
    print("=" * 60)
    print("STPA-Sec Demo Data Population")
    print("=" * 60)
    
    # Create database connection
    # Use environment variable if available, otherwise fall back to settings
    import os
    DATABASE_URL = os.getenv('DATABASE_URL', settings.database.postgres_url)
    # Convert async URL to sync URL
    SYNC_DATABASE_URL = DATABASE_URL.replace('+asyncpg', '')
    engine = create_engine(SYNC_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    
    try:
        clear_existing_data(session)
        populate_demo_data(session)
        
        print("\n" + "=" * 60)
        print("✅ Demo data population completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        session.rollback()
        import traceback
        traceback.print_exc()
    finally:
        session.close()


if __name__ == "__main__":
    main()