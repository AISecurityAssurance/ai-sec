#!/usr/bin/env python3
"""
Apply agent tables migration
"""

import asyncio
import asyncpg
import os
from pathlib import Path

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sa_user:sa_password@postgres:5432/security_analyst')

async def apply_migration():
    """Apply the agent tables migration"""
    
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("Applying Step 1 agent tables migration...")
        
        # Read migration file
        migration_path = Path(__file__).parent / "migrations" / "008_step1_agent_tables.sql"
        with open(migration_path, 'r') as f:
            migration_sql = f.read()
        
        # Apply migration
        await conn.execute(migration_sql)
        print("✓ Migration applied successfully")
        
        # Verify tables
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('agent_activity_log', 'agent_results')
            ORDER BY table_name
        """)
        
        print(f"\n✓ Created {len(tables)} agent tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Verify views
        views = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.views 
            WHERE table_schema = 'public' 
            AND table_name IN ('agent_execution_summary', 'agent_result_summary')
            ORDER BY table_name
        """)
        
        print(f"\n✓ Created {len(views)} agent views:")
        for view in views:
            print(f"  - {view['table_name']}")
        
        print("\n✓ Agent tables migration completed successfully!")
        
    except Exception as e:
        print(f"\n✗ Error applying migration: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(apply_migration())