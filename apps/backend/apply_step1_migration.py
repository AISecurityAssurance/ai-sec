#!/usr/bin/env python3
"""
Apply the STPA-Sec Step 1 migration and run tests
"""

import asyncio
import asyncpg
import os
import sys
from pathlib import Path

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sa_user:sa_password@postgres:5432/security_analyst')

async def apply_migration():
    """Apply the Step 1 migration"""
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("Applying STPA-Sec Step 1 migration...")
        print("=" * 50)
        
        # Read migration file
        migration_path = Path(__file__).parent / "migrations" / "007_stpa_sec_step1_clean.sql"
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Apply migration
        await conn.execute(migration_sql)
        print("✓ Migration applied successfully")
        
        # Verify tables exist
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'problem_statements', 'step1_losses', 'loss_dependencies',
                'step1_hazards', 'hazard_loss_mappings', 'step1_stakeholders',
                'adversary_profiles', 'mission_success_criteria',
                'step1_step2_bridge', 'problem_framing_versions'
            )
            ORDER BY table_name
        """)
        
        print(f"\n✓ Created {len(tables)} tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Verify views exist
        views = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'problem_framing_completeness', 'stakeholder_loss_matrix',
                'environmental_risk_context', 'loss_cascade_chains',
                'temporal_hazard_exposure', 'success_violation_analysis',
                'step1_executive_summary'
            )
            ORDER BY table_name
        """)
        
        print(f"\n✓ Created {len(views)} views:")
        for view in views:
            print(f"  - {view['table_name']}")
        
        # Verify function exists
        functions = await conn.fetch("""
            SELECT routine_name 
            FROM information_schema.routines
            WHERE routine_schema = 'public'
            AND routine_name = 'validate_step1_completeness'
        """)
        
        if functions:
            print(f"\n✓ Created validation function: validate_step1_completeness")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error applying migration: {e}")
        return False
    finally:
        await conn.close()

async def run_tests():
    """Run the schema tests"""
    from test_step1_schema import test_step1_schema
    await test_step1_schema()

async def main():
    """Main execution"""
    
    # Apply migration
    success = await apply_migration()
    
    if not success:
        print("\nMigration failed. Exiting.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Running schema tests...\n")
    
    # Run tests
    try:
        await run_tests()
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ Step 1 schema is ready for use!")
    print("\nNext steps:")
    print("1. Convert demo data to new schema")
    print("2. Implement Step 1 agents")
    print("3. Create API endpoints")

if __name__ == "__main__":
    asyncio.run(main())