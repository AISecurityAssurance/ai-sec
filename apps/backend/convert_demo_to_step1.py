#!/usr/bin/env python3
"""
Convert existing demo data to STPA-Sec Step 1 schema format
"""
import asyncio
import asyncpg
import json
from uuid import uuid4
from datetime import datetime
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sa_user:sa_password@postgres:5432/security_analyst')

async def clear_step1_data(conn):
    """Clear any existing Step 1 data"""
    print("Clearing existing Step 1 data...")
    
    # Delete in dependency order
    await conn.execute("DELETE FROM problem_framing_versions")
    await conn.execute("DELETE FROM step1_step2_bridge")
    await conn.execute("DELETE FROM mission_success_criteria")
    await conn.execute("DELETE FROM adversary_profiles")
    await conn.execute("DELETE FROM step1_stakeholders")
    await conn.execute("DELETE FROM hazard_loss_mappings")
    await conn.execute("DELETE FROM step1_hazards")
    await conn.execute("DELETE FROM loss_dependencies")
    await conn.execute("DELETE FROM step1_losses")
    await conn.execute("DELETE FROM problem_statements")
    await conn.execute("DELETE FROM step1_analyses")
    
    print("✓ Step 1 data cleared")

async def convert_demo_data():
    """Convert demo data to Step 1 schema format"""
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        await clear_step1_data(conn)
        
        print("\nConverting demo data to Step 1 format...")
        print("=" * 50)
        
        # 1. Create Step 1 Analysis
        analysis_id = str(uuid4())
        await conn.execute("""
            INSERT INTO step1_analyses (id, name, description, system_type, created_at)
            VALUES ($1, $2, $3, $4, $5)
        """, 
            analysis_id,
            "Digital Banking System",
            "STPA-Sec Step 1 analysis of retail and business banking platform",
            "financial_services",
            datetime.now()
        )
        print(f"✓ Created Step 1 analysis: {analysis_id}")
        
        # 2. Create Problem Statement from system definition
        system_def = await conn.fetchrow("SELECT * FROM system_definition LIMIT 1")
        if system_def:
            ps_id = str(uuid4())
            
            # Extract problem framing components from mission statement
            mission = json.loads(system_def['mission_statement']) if isinstance(system_def['mission_statement'], str) else system_def['mission_statement']
            boundaries = json.loads(system_def['system_boundaries']) if isinstance(system_def['system_boundaries'], str) else system_def['system_boundaries']
            context = json.loads(system_def['operational_context']) if isinstance(system_def['operational_context'], str) else system_def['operational_context']
            
            await conn.execute("""
                INSERT INTO problem_statements 
                (id, analysis_id, purpose_what, method_how, goals_why, 
                 mission_context, operational_constraints, environmental_assumptions)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                ps_id,
                analysis_id,
                # Purpose (what)
                "provide secure and reliable digital banking services to retail and business customers",
                # Method (how) - abstract, not implementation specific
                "controlled access to financial services with transaction integrity assurance",
                # Goals (why)
                "enable customer financial management while ensuring regulatory compliance and maintaining market trust",
                # Mission context
                json.dumps({
                    "domain": mission.get('domain', 'financial_services'),
                    "criticality": "mission_critical",
                    "scale": {
                        "geographic": "national",
                        "users": "millions",
                        "volume": "high_frequency"
                    },
                    "operational_tempo": {
                        "normal": "24x7",
                        "peak_periods": ["month_end", "holidays", "market_open"],
                        "critical_dates": ["regulatory_reporting", "audit_periods"]
                    }
                }),
                # Operational constraints
                json.dumps({
                    "regulatory": {
                        "frameworks": context.get('constraints', [])[:4] if context.get('constraints') else ["PCI-DSS", "GDPR", "CCPA", "SOX"],
                        "audit_frequency": "quarterly",
                        "change_approval": "required"
                    },
                    "business": {
                        "availability_requirement": context.get('environment', {}).get('availability', '99.99% SLA'),
                        "transaction_volume": context.get('environment', {}).get('transactions', '10M+ daily'),
                        "legacy_integration": "required"
                    },
                    "organizational": {
                        "risk_appetite": "low",
                        "security_maturity": "developing", 
                        "change_capacity": "moderate"
                    }
                }),
                # Environmental assumptions  
                json.dumps({
                    "user_behavior": ["untrusted_networks", "mobile_device_usage", "credential_sharing"],
                    "threat_landscape": boundaries.get('assumptions', [])[:3] if boundaries.get('assumptions') else ["sophisticated_adversaries", "insider_threats", "nation_state_actors"],
                    "infrastructure": ["hybrid_cloud", "third_party_dependencies", "legacy_systems"],
                    "trust_relationships": ["customer_bank", "bank_regulator", "bank_partners"]
                })
            )
            print("✓ Created problem statement")
        
        # 3. Convert Losses to Step 1 format
        losses = await conn.fetch("SELECT * FROM losses")
        loss_id_map = {}  # Map old IDs to new IDs
        
        for loss in losses:
            new_loss_id = str(uuid4())
            loss_id_map[loss['id']] = new_loss_id
            
            # Map old categories to Step 1 categories
            category_map = {
                'financial': 'financial',
                'privacy': 'privacy',
                'operational': 'mission',
                'reputation': 'reputation'
            }
            
            # Extract severity and create classification
            severity_map = {
                'critical': 'catastrophic',
                'high': 'major',
                'medium': 'moderate',
                'low': 'minor'
            }
            
            await conn.execute("""
                INSERT INTO step1_losses
                (id, analysis_id, identifier, description, loss_category, 
                 severity_classification, mission_impact)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                new_loss_id,
                analysis_id,
                loss['id'],  # Keep original identifier (L-1, L-2, etc.)
                loss['description'],
                category_map.get(loss['impact_type'], 'mission'),
                json.dumps({
                    "magnitude": severity_map.get(loss['severity'], 'major'),
                    "scope": "enterprise_wide" if loss['severity'] == 'critical' else "significant",
                    "duration": "long_term" if loss['severity'] in ['critical', 'high'] else "medium_term",
                    "reversibility": "difficult" if 'reputation' in loss['description'].lower() else "possible",
                    "detection_difficulty": "hard" if 'identity theft' in loss['description'].lower() else "moderate"
                }),
                json.dumps({
                    "primary_capability_loss": _extract_capability_loss(loss['description']),
                    "cascading_effects": loss['properties'].get('impact_areas', []),
                    "stakeholder_harm": _extract_stakeholder_harm(loss)
                })
            )
        
        print(f"✓ Converted {len(losses)} losses")
        
        # 4. Add Loss Dependencies based on impact analysis
        dependencies = [
            ('L-1', 'L-5', 'triggers', 'likely'),  # Financial loss triggers reputation damage
            ('L-2', 'L-5', 'triggers', 'certain'),  # Regulatory issues trigger reputation damage  
            ('L-3', 'L-1', 'enables', 'possible'),  # PII exposure enables financial loss
            ('L-3', 'L-5', 'triggers', 'likely'),   # PII exposure triggers reputation damage
            ('L-4', 'L-1', 'enables', 'possible'),  # Service outage enables financial loss via SLA
            ('L-4', 'L-5', 'amplifies', 'likely')   # Service outage amplifies reputation damage
        ]
        
        for primary, dependent, dep_type, strength in dependencies:
            # Find the new IDs
            primary_new = None
            dependent_new = None
            
            for old_id, new_id in loss_id_map.items():
                if old_id == primary:
                    primary_new = new_id
                if old_id == dependent:
                    dependent_new = new_id
            
            if primary_new and dependent_new:
                await conn.execute("""
                    INSERT INTO loss_dependencies
                    (id, primary_loss_id, dependent_loss_id, dependency_type, 
                     dependency_strength, time_relationship)
                    VALUES ($1, $2, $3, $4, $5, $6)
                """,
                    str(uuid4()),
                    primary_new,
                    dependent_new,
                    dep_type,
                    strength,
                    json.dumps({
                        "sequence": "immediate" if dep_type == 'triggers' else "concurrent",
                        "persistence": "sustained"
                    })
                )
        
        print("✓ Created loss dependencies")
        
        # 5. Convert Hazards to Step 1 format (system states, not mechanisms)
        hazards = await conn.fetch("SELECT * FROM hazards")
        hazard_id_map = {}
        
        for hazard in hazards:
            new_hazard_id = str(uuid4())
            hazard_id_map[hazard['id']] = new_hazard_id
            
            # Extract system state from description (remove implementation details)
            state_description = _convert_to_system_state(hazard['description'])
            
            # Determine hazard category
            category = _determine_hazard_category(hazard['description'])
            
            await conn.execute("""
                INSERT INTO step1_hazards
                (id, analysis_id, identifier, description, hazard_category,
                 affected_system_property, environmental_factors, temporal_nature)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
                new_hazard_id,
                analysis_id,
                hazard['id'],  # Keep original identifier
                state_description,
                category,
                _determine_affected_property(category),
                json.dumps({
                    "operational_conditions": {
                        "normal": {"impact": "low", "likelihood": "rare"},
                        "degraded": {"impact": "high", "likelihood": "possible"},
                        "emergency": {"impact": "catastrophic", "likelihood": "likely"}
                    },
                    "threat_conditions": {
                        "baseline": {"system_resilience": "adequate"},
                        "elevated": {"system_resilience": "stressed"},
                        "severe": {"system_resilience": "overwhelmed"}
                    }
                }),
                json.dumps({
                    "existence": "always",  # Most are persistent states
                    "mission_relevance": "critical vulnerability"
                })
            )
        
        # Special case for fraud detection hazard - temporal
        fraud_hazard = await conn.fetchrow(
            "SELECT id FROM step1_hazards WHERE identifier = 'H-5'"
        )
        if fraud_hazard:
            await conn.execute("""
                UPDATE step1_hazards 
                SET temporal_nature = $1
                WHERE id = $2
            """,
                json.dumps({
                    "existence": "periodic",
                    "when_present": "During AI model updates and batch processing windows",
                    "mission_relevance": "Creates critical vulnerability periods"
                }),
                fraud_hazard['id']
            )
        
        print(f"✓ Converted {len(hazards)} hazards to system states")
        
        # 6. Create Hazard-Loss Mappings
        mapping_count = 0
        for hazard in hazards:
            new_hazard_id = hazard_id_map[hazard['id']]
            
            for loss_ref in hazard['loss_refs']:
                if loss_ref in loss_id_map:
                    await conn.execute("""
                        INSERT INTO hazard_loss_mappings
                        (id, hazard_id, loss_id, relationship_strength, rationale)
                        VALUES ($1, $2, $3, $4, $5)
                    """,
                        str(uuid4()),
                        new_hazard_id,
                        loss_id_map[loss_ref],
                        'direct',
                        _generate_mapping_rationale(hazard['id'], loss_ref)
                    )
                    mapping_count += 1
        
        print(f"✓ Created {mapping_count} hazard-loss mappings")
        
        # 7. Convert Stakeholders (non-adversary)
        stakeholders = await conn.fetch(
            "SELECT * FROM stakeholders WHERE type != 'adversary'"
        )
        
        for stake in stakeholders:
            await conn.execute("""
                INSERT INTO step1_stakeholders
                (id, analysis_id, name, stakeholder_type, 
                 mission_perspective, loss_exposure, influence_interest)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
                str(uuid4()),
                analysis_id,
                stake['name'],
                'user' if 'Customer' in stake['name'] else 
                'regulator' if 'Regulator' in stake['name'] else
                'operator',
                json.dumps({
                    "success_means": _extract_success_perspective(stake),
                    "failure_means": _extract_failure_perspective(stake),
                    "tolerance_level": "very_low" if stake['type'] == 'primary' else "low",
                    "alternatives": "Other banks" if 'Customer' in stake['name'] else "N/A"
                }),
                json.dumps({
                    "direct_impact": _map_stakeholder_losses(stake['name']),
                    "severity_perception": _generate_severity_perception(stake['name'])
                }),
                json.dumps({
                    "influence_level": "high" if stake['type'] == 'primary' else "medium",
                    "interest_level": "high",
                    "engagement_strategy": "manage_closely" if stake['type'] == 'primary' else "keep_informed"
                })
            )
        
        print(f"✓ Converted {len(stakeholders)} stakeholders")
        
        # 8. Convert Adversaries
        adversaries = await conn.fetch("SELECT * FROM adversaries")
        
        for adv in adversaries:
            # Map motivation to adversary class
            class_map = {
                'financial': 'organized_crime',
                'espionage': 'nation_state',
                'disruption': 'hacktivist',
                'personal_gain': 'insider'
            }
            
            await conn.execute("""
                INSERT INTO adversary_profiles
                (id, analysis_id, adversary_class, profile, mission_targets)
                VALUES ($1, $2, $3, $4, $5)
            """,
                str(uuid4()),
                analysis_id,
                class_map.get(adv['motivation'], 'opportunist'),
                json.dumps({
                    "sophistication": adv['sophistication'],
                    "resources": "well_funded" if adv['sophistication'] == 'high' else "moderate",
                    "persistence": "long_term" if adv['sophistication'] == 'high' else "opportunistic",
                    "primary_interest": adv['motivation'],
                    "geographic_scope": "global" if adv['sophistication'] == 'high' else "regional"
                }),
                json.dumps({
                    "interested_in": ["customer_assets", "transaction_capability", "customer_data"],
                    "value_perception": "high_value_target",
                    "historical_interest": "known_targeting" if adv['sophistication'] == 'high' else "potential_target"
                })
            )
        
        print(f"✓ Converted {len(adversaries)} adversary profiles")
        
        # 9. Create Mission Success Criteria
        await conn.execute("""
            INSERT INTO mission_success_criteria
            (id, analysis_id, success_states, success_indicators)
            VALUES ($1, $2, $3, $4)
        """,
            str(uuid4()),
            analysis_id,
            json.dumps({
                "customer_success": {
                    "description": "Customers can reliably and securely manage their finances",
                    "violated_by_losses": ["L-1", "L-3", "L-4"],
                    "evidence_of_success": "High transaction volumes, positive customer feedback, low complaint rates"
                },
                "business_success": {
                    "description": "Bank operates profitably with sustained growth",
                    "violated_by_losses": ["L-1", "L-2", "L-4", "L-5"],
                    "evidence_of_success": "Revenue growth, customer retention, market share stability"
                },
                "regulatory_success": {
                    "description": "Operations remain compliant with all regulations",
                    "violated_by_losses": ["L-2", "L-3"],
                    "evidence_of_success": "Clean audit reports, no regulatory actions"
                },
                "security_success": {
                    "description": "System resists and recovers from attacks",
                    "violated_by_losses": ["L-1", "L-3", "L-4"],
                    "evidence_of_success": "Low incident rates, quick recovery times, threat detection"
                }
            }),
            json.dumps({
                "behavioral_indicators": [
                    "Customers actively use digital channels",
                    "Transaction volumes remain stable",
                    "New customer acquisition continues"
                ],
                "external_indicators": [
                    "Positive regulatory assessments",
                    "Industry security ratings maintained",
                    "Media coverage neutral or positive"
                ]
            })
        )
        print("✓ Created mission success criteria")
        
        # 10. Create Step 1 to Step 2 Bridge
        await conn.execute("""
            INSERT INTO step1_step2_bridge
            (id, analysis_id, control_needs, implied_boundaries)
            VALUES ($1, $2, $3, $4)
        """,
            str(uuid4()),
            analysis_id,
            json.dumps({
                "access_control": {
                    "need": "Regulate who can initiate and approve financial transactions",
                    "addresses_hazards": ["H-1", "H-2"],
                    "criticality": "essential"
                },
                "integrity_assurance": {
                    "need": "Ensure transaction authenticity and prevent tampering",
                    "addresses_hazards": ["H-2", "H-4"],
                    "criticality": "essential"
                },
                "data_protection": {
                    "need": "Protect customer information from unauthorized observation",
                    "addresses_hazards": ["H-3"],
                    "criticality": "essential"
                },
                "availability_protection": {
                    "need": "Maintain service despite disruptions",
                    "addresses_hazards": ["H-4"],
                    "criticality": "essential"
                },
                "fraud_detection": {
                    "need": "Identify and prevent illegitimate transactions",
                    "addresses_hazards": ["H-2", "H-5"],
                    "criticality": "essential"
                }
            }),
            json.dumps({
                "customer_system": {
                    "between": ["customers", "banking_platform"],
                    "nature": "service_delivery",
                    "criticality": "primary"
                },
                "system_regulator": {
                    "between": ["banking_platform", "regulators"],
                    "nature": "compliance_reporting",
                    "criticality": "required"
                },
                "system_processor": {
                    "between": ["banking_platform", "payment_networks"],
                    "nature": "transaction_processing",
                    "criticality": "essential"
                },
                "system_data": {
                    "between": ["banking_platform", "core_banking"],
                    "nature": "data_synchronization",
                    "criticality": "essential"
                }
            })
        )
        print("✓ Created Step 1 to Step 2 bridge")
        
        # Run validation
        print("\n" + "=" * 50)
        print("Running validation...")
        
        validation = await conn.fetch("""
            SELECT * FROM validate_step1_completeness($1)
        """, analysis_id)
        
        for check in validation:
            status_icon = "✓" if check['status'] == 'complete' else "⚠"
            print(f"{status_icon} {check['element']}: {check['details']}")
        
        print("\n✓ Demo data conversion complete!")
        
    except Exception as e:
        print(f"\n✗ Error during conversion: {e}")
        raise
    finally:
        await conn.close()

# Helper methods
def _extract_capability_loss(description):
    """Extract capability loss from loss description"""
    if 'unauthorized transactions' in description:
        return ["transaction_integrity", "financial_protection"]
    elif 'non-compliance' in description:
        return ["regulatory_compliance", "operational_authorization"]
    elif 'identity theft' in description:
        return ["data_protection", "privacy_assurance"]
    elif 'outage' in description:
        return ["service_availability", "customer_access"]
    elif 'reputation' in description:
        return ["market_confidence", "customer_trust"]
    return ["mission_capability"]
    
    def _extract_stakeholder_harm(self, loss):
        """Extract stakeholder harm from loss"""
        harm = {}
        if 'stake-customers' in loss.get('stakeholder_refs', []):
            harm['customers'] = {
                'type': loss['impact_type'],
                'severity': 'high' if loss['severity'] == 'critical' else 'moderate'
            }
        if 'stake-regulators' in loss.get('stakeholder_refs', []):
            harm['regulators'] = {
                'type': 'compliance_failure',
                'severity': 'critical'
            }
        harm['organization'] = {
            'type': loss['impact_type'],
            'severity': loss['severity']
        }
        return harm
    
    def _convert_to_system_state(self, description):
        """Convert hazard description to system state (remove implementation details)"""
        # Map implementation-specific descriptions to system states
        state_map = {
            'Authentication system accepts invalid credentials': 
                'System operates with compromised authentication integrity',
            'Transaction authorization system fails to verify': 
                'System operates without transaction authorization integrity',
            'Database encryption keys exposed': 
                'System operates with data protection mechanisms compromised',
            'Core banking integration unavailable': 
                'System operates in disconnected state without backend synchronization',
            'AI fraud detection providing false negatives': 
                'System operates without effective fraud detection capability'
        }
        
        for impl_desc, state_desc in state_map.items():
            if impl_desc in description:
                return state_desc
        
        return f"System operates in compromised state: {description}"
    
    def _determine_hazard_category(self, description):
        """Determine hazard category from description"""
        desc_lower = description.lower()
        if 'authentication' in desc_lower or 'authorization' in desc_lower:
            return 'integrity_compromised'
        elif 'encryption' in desc_lower or 'data' in desc_lower:
            return 'confidentiality_breached'
        elif 'unavailable' in desc_lower or 'outage' in desc_lower:
            return 'availability_degraded'
        elif 'fraud' in desc_lower:
            return 'capability_loss'
        return 'mission_degraded'
    
    def _determine_affected_property(self, category):
        """Map category to affected system property"""
        property_map = {
            'integrity_compromised': 'transaction_integrity',
            'confidentiality_breached': 'data_protection',
            'availability_degraded': 'service_availability',
            'capability_loss': 'operational_capability',
            'mission_degraded': 'mission_effectiveness'
        }
        return property_map.get(category, 'mission_effectiveness')
    
    def _generate_mapping_rationale(self, hazard_id, loss_id):
        """Generate rationale for hazard-loss mapping"""
        rationales = {
            ('H-1', 'L-1'): "Compromised authentication directly enables unauthorized financial transactions",
            ('H-1', 'L-3'): "Authentication compromise exposes customer accounts and personal data",
            ('H-2', 'L-1'): "Failed transaction authorization allows illegitimate financial transfers",
            ('H-2', 'L-2'): "Authorization failures violate regulatory transaction controls",
            ('H-3', 'L-3'): "Compromised data protection directly exposes customer PII",
            ('H-3', 'L-2'): "Data breaches violate privacy regulations",
            ('H-3', 'L-5'): "Major data breaches severely damage customer trust",
            ('H-4', 'L-4'): "System unavailability directly prevents customer fund access",
            ('H-4', 'L-5'): "Extended outages damage bank reliability perception",
            ('H-5', 'L-1'): "Ineffective fraud detection fails to prevent financial losses",
            ('H-5', 'L-2'): "Failed fraud detection violates regulatory requirements"
        }
        return rationales.get((hazard_id, loss_id), "System state enables loss occurrence")
    
    def _extract_success_perspective(self, stakeholder):
        """Extract what success means to stakeholder"""
        name = stakeholder['name']
        if 'Customer' in name:
            return "I can access and manage my money safely whenever I need to"
        elif 'Regulator' in name:
            return "The bank operates within legal boundaries and protects consumers"
        elif 'Employee' in name:
            return "I can effectively serve customers with secure, reliable tools"
        return "The system operates effectively for its intended purpose"
    
    def _extract_failure_perspective(self, stakeholder):
        """Extract what failure means to stakeholder"""
        name = stakeholder['name']
        if 'Customer' in name:
            return "I lose money or cannot access my funds when needed"
        elif 'Regulator' in name:
            return "The bank violates regulations or harms consumers"
        elif 'Employee' in name:
            return "I cannot do my job or the bank's reputation is damaged"
        return "The system fails to achieve its mission"
    
    def _map_stakeholder_losses(self, stakeholder_name):
        """Map stakeholder to losses that affect them"""
        if 'Customer' in stakeholder_name:
            return ["L-1", "L-3", "L-4"]
        elif 'Business' in stakeholder_name:
            return ["L-1", "L-4", "L-5"]
        elif 'Regulator' in stakeholder_name:
            return ["L-2", "L-3"]
        elif 'Employee' in stakeholder_name:
            return ["L-5"]
        return []
    
    def _generate_severity_perception(self, stakeholder_name):
        """Generate severity perception for losses"""
        if 'Customer' in stakeholder_name:
            return {
                "L-1": "catastrophic",
                "L-3": "catastrophic", 
                "L-4": "major"
            }
        elif 'Business' in stakeholder_name:
            return {
                "L-1": "catastrophic",
                "L-4": "major",
                "L-5": "major"
            }
        elif 'Regulator' in stakeholder_name:
            return {
                "L-2": "catastrophic",
                "L-3": "major"
            }
        return {}

if __name__ == "__main__":
    asyncio.run(convert_demo_data())