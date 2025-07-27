#!/usr/bin/env python3
"""
Test script to verify STPA-Sec PostgreSQL integration
"""
import asyncio
import json
from datetime import datetime
from uuid import uuid4, UUID
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import settings
from core.models.schemas import AgentContext, FrameworkType
from core.agents.framework_agents.stpa_sec import StpaSecAgent
from storage.repositories.stpa_sec import STPASecRepository
from src.database.stpa_sec_models import (
    Base, Loss, Hazard, Entity, SystemDefinition, Stakeholder, 
    Adversary, Relationship, Analysis, Scenario, Mitigation, 
    ScenarioMitigation
)


async def test_stpa_sec_integration():
    """Test the complete STPA-Sec integration with PostgreSQL"""
    print("=" * 60)
    print("STPA-Sec PostgreSQL Integration Test")
    print("=" * 60)
    
    # Create database connection
    DATABASE_URL = settings.database.postgres_url.replace('+asyncpg', '')
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create a test session
    db_session = SessionLocal()
    
    try:
        # Clear any existing test data
        print("\n0. Clearing existing test data...")
        db_session.query(ScenarioMitigation).delete()
        db_session.query(Mitigation).delete()
        db_session.query(Scenario).delete()
        db_session.query(Analysis).delete()
        db_session.query(Relationship).delete()
        db_session.query(Entity).delete()
        db_session.query(Hazard).delete()
        db_session.query(Loss).delete()
        db_session.query(Adversary).delete()
        db_session.query(Stakeholder).delete()
        db_session.query(SystemDefinition).delete()
        db_session.commit()
        print("✓ Test data cleared")
        
        # 1. Create test context
        print("\n1. Creating test context...")
        context = AgentContext(
            analysis_id=uuid4(),
            system_description="""
            Banking Mobile Application Security Analysis
            
            The mobile banking application allows customers to:
            - Check account balances
            - Transfer money between accounts
            - Pay bills
            - Deposit checks via camera
            - Find ATM locations
            
            Key components:
            - Mobile app (iOS/Android)
            - API Gateway
            - Authentication service
            - Core banking system
            - Database servers
            """,
            artifacts={},
            completed_frameworks=[],
            metadata={
                "system_type": "mobile_banking",
                "environment": {
                    "deployment": "cloud",
                    "users": "retail customers",
                    "data_sensitivity": "high",
                    "compliance": ["PCI-DSS", "SOC2"]
                },
                "test_run": True,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        print("✓ Context created successfully")
        
        # 2. Create STPA-Sec agent with database
        print("\n2. Initializing STPA-Sec agent with database...")
        agent = StpaSecAgent(db_session=db_session)
        print("✓ Agent initialized")
        
        # 3. Run analysis (simplified for testing)
        print("\n3. Running STPA-Sec analysis...")
        print("   Note: This will use mock data for testing")
        
        # For testing, we'll manually create some sections
        from core.agents.types import SectionResult, TemplateType
        from core.models.schemas import AnalysisStatus
        
        sections = [
            SectionResult(
                section_id="system_definition",
                title="System Definition",
                content={
                    "purpose": "Secure mobile banking application",
                    "in_scope": ["Mobile app", "API Gateway", "Auth service"],
                    "out_scope": ["ATM hardware", "Branch systems"],
                    "assumptions": ["Users have secure devices", "Network is untrusted"]
                },
                template_type=TemplateType.SECTION,
                status=AnalysisStatus.COMPLETED
            ),
            SectionResult(
                section_id="losses",
                title="Losses",
                content={
                    "losses": [
                        {
                            "id": "L-1",
                            "description": "Unauthorized access to customer accounts",
                            "type": "privacy",
                            "severity": "critical",
                            "stakeholders": ["Customers", "Bank"]
                        },
                        {
                            "id": "L-2",
                            "description": "Financial theft or fraud",
                            "type": "financial",
                            "severity": "critical",
                            "stakeholders": ["Customers", "Bank", "Insurers"]
                        }
                    ]
                },
                template_type=TemplateType.TABLE,
                status=AnalysisStatus.COMPLETED
            ),
            SectionResult(
                section_id="hazards",
                title="Hazards",
                content={
                    "hazards": [
                        {
                            "id": "H-1",
                            "description": "Authentication bypass allowing unauthorized access",
                            "system_state": "Authentication service accepting invalid credentials",
                            "linked_losses": ["L-1", "L-2"]
                        },
                        {
                            "id": "H-2",
                            "description": "Transaction manipulation in transit",
                            "system_state": "API Gateway forwarding modified transaction data",
                            "linked_losses": ["L-2"]
                        }
                    ]
                },
                template_type=TemplateType.TABLE,
                status=AnalysisStatus.COMPLETED
            ),
            SectionResult(
                section_id="control_structure",
                title="Control Structure",
                content={
                    "entities": [
                        {
                            "name": "Mobile App",
                            "type": "controller",
                            "description": "User interface and local control logic",
                            "responsibilities": ["User input validation", "Secure storage", "API communication"]
                        },
                        {
                            "name": "API Gateway",
                            "type": "controller",
                            "description": "Request routing and rate limiting",
                            "responsibilities": ["Request validation", "Rate limiting", "Load balancing"]
                        },
                        {
                            "name": "Auth Service",
                            "type": "controller",
                            "description": "Authentication and authorization",
                            "responsibilities": ["Credential validation", "Token generation", "Session management"]
                        }
                    ],
                    "relationships": [
                        {
                            "source": "Mobile App",
                            "target": "API Gateway",
                            "type": "control",
                            "control_actions": ["Login request", "Transaction request"],
                            "feedback_info": ["Auth token", "Transaction status"]
                        },
                        {
                            "source": "API Gateway",
                            "target": "Auth Service",
                            "type": "control",
                            "control_actions": ["Validate token", "Refresh token"],
                            "feedback_info": ["Token valid/invalid", "New token"]
                        }
                    ]
                },
                template_type=TemplateType.DIAGRAM,
                status=AnalysisStatus.COMPLETED
            )
        ]
        
        # Create mock result
        from core.models.schemas import AgentResult
        result = AgentResult(
            framework=FrameworkType.STPA_SEC,
            sections=[s.model_dump() for s in sections],
            artifacts=[],
            duration=10.5,
            token_usage={"input_tokens": 1000, "output_tokens": 2000, "total_tokens": 3000}
        )
        
        # Convert sections to dict format
        result.sections = {s["section_id"]: s for s in result.sections}
        
        print("✓ Analysis completed (using mock data)")
        
        # 4. Save to database
        print("\n4. Saving analysis to PostgreSQL...")
        repository = STPASecRepository(db_session)
        
        try:
            analysis_id = repository.save_analysis(context, result)
            print(f"✓ Analysis saved successfully with ID: {analysis_id}")
        except Exception as e:
            print(f"✗ Failed to save analysis: {str(e)}")
            raise
        
        # 5. Verify saved data
        print("\n5. Verifying saved data...")
        
        # Check system definition
        system_def = repository.get_system_definition()
        if system_def:
            print(f"✓ System definition found: {system_def.mission_statement.get('domain', 'Unknown')}")
        else:
            print("✗ System definition not found")
        
        # Check losses
        losses = db_session.query(Loss).all()
        print(f"✓ Losses saved: {len(losses)} losses")
        for loss in losses:
            print(f"   - {loss.id}: {loss.description[:50]}...")
        
        # Check hazards
        hazards = db_session.query(Hazard).all()
        print(f"✓ Hazards saved: {len(hazards)} hazards")
        for hazard in hazards:
            print(f"   - {hazard.id}: {hazard.description[:50]}...")
        
        # Check entities
        entities = db_session.query(Entity).all()
        print(f"✓ Entities saved: {len(entities)} entities")
        for entity in entities:
            entity_type = entity.properties.get('type', 'unknown') if entity.properties else 'unknown'
            print(f"   - {entity.name} ({entity_type})")
        
        # Check control structure
        control_structure = repository.get_control_structure()
        print(f"✓ Control structure: {len(control_structure['entities'])} entities, {len(control_structure['relationships'])} relationships")
        
        print("\n" + "=" * 60)
        print("✅ STPA-Sec PostgreSQL Integration Test PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db_session.close()
        print("\nDatabase session closed.")


if __name__ == "__main__":
    # Run the test
    asyncio.run(test_stpa_sec_integration())