#!/usr/bin/env python3
"""
Database setup script - creates database and user if they don't exist
"""

import psycopg2
from psycopg2 import sql
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings

def setup_database():
    """Create database and user if they don't exist"""
    
    db_config = settings.database
    
    print("Setting up database...")
    print(f"Host: {db_config.postgres_host}")
    print(f"Port: {db_config.postgres_port}")
    print(f"Database: {db_config.postgres_db}")
    print(f"User: {db_config.postgres_user}")
    
    try:
        # Connect to PostgreSQL as superuser (usually 'postgres')
        # You may need to adjust these credentials for your system
        print("\nConnecting to PostgreSQL...")
        conn = psycopg2.connect(
            host=db_config.postgres_host,
            port=db_config.postgres_port,
            user='postgres',  # Default superuser
            password=os.getenv('POSTGRES_SUPERUSER_PASSWORD', 'postgres'),
            database='postgres'  # Connect to default database
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute(
            "SELECT 1 FROM pg_user WHERE usename = %s",
            (db_config.postgres_user,)
        )
        
        if not cursor.fetchone():
            print(f"\nCreating user '{db_config.postgres_user}'...")
            cursor.execute(
                sql.SQL("CREATE USER {} WITH PASSWORD %s").format(
                    sql.Identifier(db_config.postgres_user)
                ),
                (db_config.postgres_password,)
            )
            print("✓ User created")
        else:
            print(f"\n✓ User '{db_config.postgres_user}' already exists")
        
        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_config.postgres_db,)
        )
        
        if not cursor.fetchone():
            print(f"\nCreating database '{db_config.postgres_db}'...")
            cursor.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(
                    sql.Identifier(db_config.postgres_db),
                    sql.Identifier(db_config.postgres_user)
                )
            )
            print("✓ Database created")
        else:
            print(f"\n✓ Database '{db_config.postgres_db}' already exists")
        
        # Grant privileges
        print("\nGranting privileges...")
        cursor.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(db_config.postgres_db),
                sql.Identifier(db_config.postgres_user)
            )
        )
        print("✓ Privileges granted")
        
        cursor.close()
        conn.close()
        
        print("\n✓ Database setup completed successfully!")
        print("\nYou can now run: python test_database_setup.py")
        return True
        
    except psycopg2.Error as e:
        print(f"\n✗ Database setup failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check if you can connect as 'postgres' user")
        print("3. You may need to set POSTGRES_SUPERUSER_PASSWORD environment variable")
        print("4. On some systems, you may need to run: sudo -u postgres psql")
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = setup_database()
    sys.exit(0 if success else 1)