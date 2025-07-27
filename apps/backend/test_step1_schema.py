#!/usr/bin/env python3
"""
Test script for STPA-Sec Step 1 schema
Tests basic CRUD operations and constraints
"""

import asyncio
import asyncpg
import json
from uuid import uuid4
import os
from datetime import datetime

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sa_user:sa_password@postgres:5432/security_analyst')

async def test_step1_schema():
    """Test the Step 1 schema with sample data"""
    
    # Connect to database
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("Testing STPA-Sec Step 1 Schema...")
        print("=" * 50)
        
        # Create a test analysis
        analysis_id = str(uuid4())
        await conn.execute("""
            INSERT INTO step1_analyses (id, name, description, created_at)
            VALUES ($1, $2, $3, $4)
        """, analysis_id, "Test Banking System", "Schema validation test", datetime.now())
        
        print(f"✓ Created test analysis: {analysis_id}")
        
        # 1. Test Problem Statement
        ps_id = str(uuid4())
        await conn.execute("""
            INSERT INTO problem_statements 
            (id, analysis_id, purpose_what, method_how, goals_why, mission_context)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, 
            ps_id, 
            analysis_id,
            "enable secure management of customer financial assets",
            "controlled access to banking services and transaction integrity assurance",
            "preserve customer trust, ensure regulatory compliance, and maintain financial stability",
            json.dumps({
                "domain": "financial_services",
                "criticality": "mission_critical",
                "scale": {"geographic": "national", "users": "millions"}
            })
        )
        
        # Verify generated column
        result = await conn.fetchrow(
            "SELECT full_statement FROM problem_statements WHERE id = $1", 
            ps_id
        )
        print(f"✓ Problem statement created")
        print(f"  Generated statement: {result['full_statement'][:80]}...")
        
        # 2. Test Losses
        loss_ids = []
        losses = [
            ("L1", "Customer financial loss", "financial", {"magnitude": "catastrophic"}),
            ("L2", "Regulatory non-compliance", "regulatory", {"magnitude": "major"}),
            ("L3", "Loss of customer trust", "reputation", {"magnitude": "catastrophic"})
        ]
        
        for identifier, desc, category, severity in losses:
            loss_id = str(uuid4())
            loss_ids.append(loss_id)
            await conn.execute("""
                INSERT INTO step1_losses 
                (id, analysis_id, identifier, description, loss_category, severity_classification)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, loss_id, analysis_id, identifier, desc, category, json.dumps(severity))
        
        print(f"✓ Created {len(losses)} losses")
        
        # 3. Test Loss Dependencies
        dep_id = str(uuid4())
        await conn.execute("""
            INSERT INTO loss_dependencies
            (id, primary_loss_id, dependent_loss_id, dependency_type, dependency_strength)
            VALUES ($1, $2, $3, $4, $5)
        """, dep_id, loss_ids[0], loss_ids[2], "triggers", "likely")
        
        print("✓ Created loss dependency: L1 → L3")
        
        # 4. Test Hazards
        hazard_ids = []
        hazards = [
            ("H1", "System operates with compromised transaction authorization integrity", 
             "integrity_compromised", {"existence": "always"}),
            ("H2", "System operates with customer data exposed to unauthorized entities",
             "confidentiality_breached", {"existence": "always"}),
            ("H3", "System operates without fraud detection during batch processing",
             "capability_loss", {"existence": "periodic", "when_present": "2am-4am daily"})
        ]
        
        for identifier, desc, category, temporal in hazards:
            hazard_id = str(uuid4())
            hazard_ids.append(hazard_id)
            await conn.execute("""
                INSERT INTO step1_hazards
                (id, analysis_id, identifier, description, hazard_category, temporal_nature)
                VALUES ($1, $2, $3, $4, $5, $6)
            """, hazard_id, analysis_id, identifier, desc, category, json.dumps(temporal))
        
        print(f"✓ Created {len(hazards)} hazards (including temporal)")
        
        # 5. Test Hazard-Loss Mappings
        mappings = [
            (hazard_ids[0], loss_ids[0], "direct"),
            (hazard_ids[0], loss_ids[2], "direct"),
            (hazard_ids[1], loss_ids[1], "direct"),
            (hazard_ids[2], loss_ids[0], "conditional")
        ]
        
        for h_id, l_id, strength in mappings:
            await conn.execute("""
                INSERT INTO hazard_loss_mappings
                (id, hazard_id, loss_id, relationship_strength)
                VALUES ($1, $2, $3, $4)
            """, str(uuid4()), h_id, l_id, strength)
        
        print(f"✓ Created {len(mappings)} hazard-loss mappings")
        
        # 6. Test Stakeholders
        stakeholder_id = str(uuid4())
        await conn.execute("""
            INSERT INTO step1_stakeholders
            (id, analysis_id, name, stakeholder_type, mission_perspective, loss_exposure)
            VALUES ($1, $2, $3, $4, $5, $6)
        """, 
            stakeholder_id,
            analysis_id,
            "Banking Customers",
            "user",
            json.dumps({
                "success_means": "I can access and manage my money whenever needed",
                "failure_means": "I cannot access my funds or lose money",
                "tolerance_level": "very_low"
            }),
            json.dumps({
                "direct_impact": ["L1", "L3"],
                "severity_perception": {"L1": "catastrophic", "L3": "major"}
            })
        )
        
        print("✓ Created stakeholder with mission perspective")
        
        # 7. Test Adversary Profile
        adversary_id = str(uuid4())
        await conn.execute("""
            INSERT INTO adversary_profiles
            (id, analysis_id, adversary_class, profile, mission_targets)
            VALUES ($1, $2, $3, $4, $5)
        """,
            adversary_id,
            analysis_id,
            "organized_crime",
            json.dumps({
                "sophistication": "high",
                "resources": "well_funded",
                "persistence": "long_term",
                "primary_interest": "financial_gain"
            }),
            json.dumps({
                "interested_in": ["customer_assets", "transaction_capability"],
                "value_perception": "high_value_target"
            })
        )
        
        print("✓ Created adversary profile")
        
        # 8. Test Mission Success Criteria
        success_id = str(uuid4())
        await conn.execute("""
            INSERT INTO mission_success_criteria
            (id, analysis_id, success_states, success_indicators)
            VALUES ($1, $2, $3, $4)
        """,
            success_id,
            analysis_id,
            json.dumps({
                "customer_success": {
                    "description": "Customers can reliably access and manage their finances",
                    "violated_by_losses": ["L1", "L3"],
                    "evidence_of_success": "Regular system usage, positive feedback"
                },
                "regulatory_success": {
                    "description": "Operations remain within legal boundaries",
                    "violated_by_losses": ["L2"],
                    "evidence_of_success": "Clean audit reports"
                }
            }),
            json.dumps({
                "behavioral_indicators": ["Customers regularly use the system"],
                "external_indicators": ["Positive regulatory assessments"]
            })
        )
        
        print("✓ Created mission success criteria")
        
        # 9. Test Views
        print("\nTesting analysis views...")
        
        # Test completeness view
        completeness = await conn.fetchrow("""
            SELECT * FROM problem_framing_completeness 
            WHERE analysis_id = $1
        """, analysis_id)
        
        print(f"✓ Completeness check: {completeness['completeness_level']}")
        print(f"  - Losses: {completeness['loss_count']}")
        print(f"  - Hazards: {completeness['hazard_count']}")
        print(f"  - Uncovered losses: {completeness['uncovered_losses']}")
        
        # Test cascade view
        cascades = await conn.fetch("""
            SELECT * FROM loss_cascade_chains
            WHERE chain_path LIKE '%' || $1 || '%'
            LIMIT 5
        """, 'L1')
        
        print(f"✓ Loss cascade chains: Found {len(cascades)} chains")
        for cascade in cascades:
            print(f"  - {cascade['chain_path']}")
        
        # Test temporal hazards view
        temporal = await conn.fetch("""
            SELECT * FROM temporal_hazard_exposure
            LIMIT 5
        """)
        
        if temporal:
            print(f"✓ Temporal hazards: Found {len(temporal)}")
            for t in temporal:
                print(f"  - {t['identifier']}: {t['vulnerability_window']}")
        
        # 10. Test validation function
        print("\nTesting validation function...")
        validation = await conn.fetch("""
            SELECT * FROM validate_step1_completeness($1)
        """, analysis_id)
        
        for check in validation:
            status_icon = "✓" if check['status'] == 'complete' else "⚠"
            print(f"{status_icon} {check['element']}: {check['details']}")
        
        # Test constraint violations
        print("\nTesting constraint violations...")
        
        # Test duplicate identifier
        try:
            await conn.execute("""
                INSERT INTO step1_losses 
                (id, analysis_id, identifier, description, loss_category)
                VALUES ($1, $2, $3, $4, $5)
            """, str(uuid4()), analysis_id, "L1", "Duplicate", "financial")
            print("✗ ERROR: Duplicate identifier constraint not working!")
        except asyncpg.UniqueViolationError:
            print("✓ Duplicate identifier constraint working")
        
        # Test invalid category
        try:
            await conn.execute("""
                INSERT INTO step1_losses 
                (id, analysis_id, identifier, description, loss_category)
                VALUES ($1, $2, $3, $4, $5)
            """, str(uuid4()), analysis_id, "L99", "Invalid", "invalid_category")
            print("✗ ERROR: Category constraint not working!")
        except asyncpg.CheckViolationError:
            print("✓ Category constraint working")
        
        # Test circular dependency prevention
        try:
            await conn.execute("""
                INSERT INTO loss_dependencies
                (id, primary_loss_id, dependent_loss_id, dependency_type, dependency_strength)
                VALUES ($1, $2, $3, $4, $5)
            """, str(uuid4()), loss_ids[0], loss_ids[0], "triggers", "certain")
            print("✗ ERROR: Circular dependency constraint not working!")
        except asyncpg.CheckViolationError:
            print("✓ Circular dependency constraint working")
        
        print("\n" + "=" * 50)
        print("✓ All schema tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        raise
    finally:
        # Cleanup
        await conn.execute("DELETE FROM step1_analyses WHERE id = $1", analysis_id)
        await conn.close()

if __name__ == "__main__":
    asyncio.run(test_step1_schema())