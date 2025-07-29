#!/usr/bin/env python3
"""
Test script to verify database setup and migrations
"""

import asyncio
import sys
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
import asyncpg
from datetime import datetime

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from src.database.stpa_sec_models import Base, SystemDefinition, Adversary, ControlLoop, Entity
from src.database.demo_data_migration import DemoDataMigrator

class DatabaseTester:
    def __init__(self):
        self.db_config = settings.database
        self.sync_url = self.db_config.postgres_url.replace('+asyncpg', '')
        
    async def test_connection(self):
        """Test basic database connection"""
        print("1. Testing database connection...")
        try:
            # Test raw connection
            conn = await asyncpg.connect(
                host=self.db_config.postgres_host,
                port=self.db_config.postgres_port,
                user=self.db_config.postgres_user,
                password=self.db_config.postgres_password,
                database=self.db_config.postgres_db
            )
            version = await conn.fetchval('SELECT version()')
            print(f"   ✓ Connected to PostgreSQL: {version}")
            await conn.close()
            return True
        except Exception as e:
            print(f"   ✗ Connection failed: {e}")
            return False
    
    async def run_migrations(self):
        """Run all migration files"""
        print("\n2. Running migrations...")
        
        migrations_dir = Path(__file__).parent / 'migrations'
        migration_files = sorted(migrations_dir.glob('*.sql'))
        
        if not migration_files:
            print("   ✗ No migration files found!")
            return False
            
        try:
            # Create synchronous engine for migrations
            engine = create_engine(self.sync_url)
            
            with engine.connect() as conn:
                for migration_file in migration_files:
                    print(f"   Running {migration_file.name}...")
                    
                    # Read and execute migration
                    sql_content = migration_file.read_text()
                    
                    # Split by semicolons but be careful with functions
                    statements = []
                    current = []
                    in_function = False
                    
                    for line in sql_content.split('\n'):
                        if 'CREATE OR REPLACE FUNCTION' in line or 'CREATE FUNCTION' in line:
                            in_function = True
                        if line.strip() == '$$ LANGUAGE plpgsql;':
                            in_function = False
                            current.append(line)
                            statements.append('\n'.join(current))
                            current = []
                            continue
                        
                        current.append(line)
                        
                        if not in_function and line.strip().endswith(';'):
                            statements.append('\n'.join(current))
                            current = []
                    
                    # Execute each statement
                    for statement in statements:
                        if statement.strip():
                            try:
                                conn.execute(text(statement))
                                conn.commit()
                            except Exception as e:
                                conn.rollback()  # Rollback the failed transaction
                                if 'already exists' in str(e):
                                    print(f"      (skipping - already exists)")
                                else:
                                    print(f"      Error: {e}")
                                    raise
                    
                    print(f"   ✓ {migration_file.name} completed")
                    
            print("   ✓ All migrations completed successfully")
            return True
            
        except Exception as e:
            print(f"   ✗ Migration failed: {e}")
            return False
    
    async def verify_tables(self):
        """Verify all tables were created"""
        print("\n3. Verifying tables...")
        
        expected_tables = [
            'system_definition',
            'adversaries', 
            'control_loops',
            'entities',
            'relationships',
            'control_actions',
            'feedback_mechanisms',
            'process_models',
            'unsafe_control_actions',
            'loss_scenarios',
            'initial_mitigations',
            'stride_analysis',
            'framework_mappings',
            'analysis_sessions',
            'analysis_results',
            'temporal_phases',
            'adversarial_ucas',
            'wargaming_sessions',
            'cve_database',
            'entity_vulnerabilities'
        ]
        
        try:
            conn = await asyncpg.connect(
                host=self.db_config.postgres_host,
                port=self.db_config.postgres_port,
                user=self.db_config.postgres_user,
                password=self.db_config.postgres_password,
                database=self.db_config.postgres_db
            )
            
            # Get all tables
            tables = await conn.fetch("""
                SELECT tablename 
                FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """)
            
            existing_tables = {row['tablename'] for row in tables}
            
            missing_tables = []
            for table in expected_tables:
                if table in existing_tables:
                    print(f"   ✓ {table}")
                else:
                    print(f"   ✗ {table} (missing)")
                    missing_tables.append(table)
            
            await conn.close()
            
            if missing_tables:
                print(f"\n   Missing tables: {', '.join(missing_tables)}")
                return False
            else:
                print("\n   ✓ All expected tables exist")
                return True
                
        except Exception as e:
            print(f"   ✗ Table verification failed: {e}")
            return False
    
    async def test_functions(self):
        """Test database functions"""
        print("\n4. Testing database functions...")
        
        try:
            conn = await asyncpg.connect(
                host=self.db_config.postgres_host,
                port=self.db_config.postgres_port,
                user=self.db_config.postgres_user,
                password=self.db_config.postgres_password,
                database=self.db_config.postgres_db
            )
            
            # Test calculate_trust_boundary_risk
            print("   Testing calculate_trust_boundary_risk()...")
            result = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_proc 
                    WHERE proname = 'calculate_trust_boundary_risk'
                )
            """)
            if result:
                print("   ✓ calculate_trust_boundary_risk exists")
            else:
                print("   ✗ calculate_trust_boundary_risk missing")
            
            # Test propagate_compromise
            print("   Testing propagate_compromise()...")
            result = await conn.fetchval("""
                SELECT EXISTS (
                    SELECT 1 FROM pg_proc 
                    WHERE proname = 'propagate_compromise'
                )
            """)
            if result:
                print("   ✓ propagate_compromise exists")
            else:
                print("   ✗ propagate_compromise missing")
                
            await conn.close()
            return True
            
        except Exception as e:
            print(f"   ✗ Function testing failed: {e}")
            return False
    
    async def insert_test_data(self):
        """Insert test data using SQLAlchemy models"""
        print("\n5. Inserting test data...")
        
        try:
            # Create sync engine for the migrator
            sync_engine = create_engine(self.sync_url)
            
            # Create demo data migration
            # Create a session for the migrator
            from sqlalchemy.orm import sessionmaker
            Session = sessionmaker(bind=sync_engine)
            session = Session()
            
            migration = DemoDataMigrator(session)
            
            # Run the migration with demo data
            print("   Running demo data migration...")
            demo_data = {}  # Empty dict as the migrator uses internal demo data
            result = migration.migrate_all(demo_data)
            
            print("   ✓ Test data inserted successfully")
            return True
            
        except Exception as e:
            print(f"   ✗ Test data insertion failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def verify_data(self):
        """Verify test data was inserted correctly"""
        print("\n6. Verifying test data...")
        
        try:
            conn = await asyncpg.connect(
                host=self.db_config.postgres_host,
                port=self.db_config.postgres_port,
                user=self.db_config.postgres_user,
                password=self.db_config.postgres_password,
                database=self.db_config.postgres_db
            )
            
            # Check system definitions
            systems = await conn.fetch("SELECT id, mission_statement FROM system_definition")
            print(f"   Systems: {len(systems)}")
            for system in systems:
                mission = system['mission_statement']
                print(f"     - System {system['id']}: {mission.get('primary_mission', 'No mission') if isinstance(mission, dict) else mission}")
            
            # Check adversaries
            adversaries = await conn.fetch("SELECT name, sophistication FROM adversaries")
            print(f"   Adversaries: {len(adversaries)}")
            for adv in adversaries:
                print(f"     - {adv['name']} ({adv['sophistication']})")
            
            # Check entities
            entities = await conn.fetch("SELECT name, type FROM entities")
            print(f"   Entities: {len(entities)}")
            
            # Check control loops
            loops = await conn.fetch("SELECT name FROM control_loops")
            print(f"   Control Loops: {len(loops)}")
            
            # Check UCAs
            ucas = await conn.fetch("SELECT type, context FROM unsafe_control_actions")
            print(f"   UCAs: {len(ucas)}")
            
            await conn.close()
            
            if systems and adversaries and entities and loops:
                print("\n   ✓ Test data verified successfully")
                return True
            else:
                print("\n   ✗ Test data incomplete")
                return False
                
        except Exception as e:
            print(f"   ✗ Data verification failed: {e}")
            return False
    
    async def run_all_tests(self):
        """Run all database tests"""
        print("=" * 60)
        print("DATABASE SETUP AND TESTING")
        print("=" * 60)
        
        results = {
            "Connection": await self.test_connection(),
            "Migrations": await self.run_migrations(),
            "Tables": await self.verify_tables(),
            "Functions": await self.test_functions(),
            "Test Data": await self.insert_test_data(),
            "Verification": await self.verify_data()
        }
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        
        all_passed = True
        for test, passed in results.items():
            status = "✓ PASSED" if passed else "✗ FAILED"
            print(f"{test:.<40} {status}")
            if not passed:
                all_passed = False
        
        print("=" * 60)
        
        if all_passed:
            print("\n✓ All database tests passed! The database is ready to use.")
        else:
            print("\n✗ Some tests failed. Please check the errors above.")
        
        return all_passed


if __name__ == "__main__":
    tester = DatabaseTester()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)