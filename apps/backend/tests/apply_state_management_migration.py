#!/usr/bin/env python3
"""Apply state management migration"""
import asyncio
import asyncpg
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://sa_user:sa_password@postgres:5432/security_analyst')

async def apply_migration():
    """Apply the state management migration"""
    
    # Connect to database
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        print("Applying state management migration...")
        
        # Read migration file
        with open('migrations/009_state_management.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        await conn.execute(migration_sql)
        
        print("✓ State management tables created successfully!")
        
        # Verify tables were created
        tables = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('analysis_drafts', 'analysis_versions', 'element_dependencies')
            ORDER BY table_name
        """)
        
        print("\nCreated tables:")
        for table in tables:
            print(f"  - {table['table_name']}")
        
        # Verify views
        views = await conn.fetch("""
            SELECT table_name 
            FROM information_schema.views
            WHERE table_schema = 'public'
            AND table_name IN ('latest_analysis_versions', 'active_drafts')
            ORDER BY table_name
        """)
        
        print("\nCreated views:")
        for view in views:
            print(f"  - {view['table_name']}")
            
    except Exception as e:
        print(f"✗ Error applying migration: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(apply_migration())