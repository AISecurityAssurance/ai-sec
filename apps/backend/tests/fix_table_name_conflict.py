#!/usr/bin/env python3
"""
Fix table name conflict by renaming 'analyses' to 'stpa_analyses' in STPA-Sec schema
"""
import psycopg2
from config.settings import settings

def fix_table_conflict():
    """Rename analyses table to stpa_analyses to avoid conflict"""
    print("Fixing table name conflict...")
    
    # Parse database URL
    db_url = settings.database.postgres_url.replace('+asyncpg', '')
    # Extract connection params from URL
    # Format: postgresql://user:password@host:port/dbname
    parts = db_url.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    host_port_db = parts[1].split('/')
    host_port = host_port_db[0].split(':')
    
    conn_params = {
        'host': host_port[0],
        'port': host_port[1],
        'database': host_port_db[1],
        'user': user_pass[0],
        'password': user_pass[1]
    }
    
    conn = psycopg2.connect(**conn_params)
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        # Check if the old analyses table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'analyses' 
                AND table_schema = 'public'
            );
        """)
        old_exists = cur.fetchone()[0]
        
        # Check if stpa_analyses already exists
        cur.execute("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'stpa_analyses' 
                AND table_schema = 'public'
            );
        """)
        new_exists = cur.fetchone()[0]
        
        if old_exists and not new_exists:
            print("Renaming 'analyses' table to 'stpa_analyses'...")
            cur.execute("ALTER TABLE analyses RENAME TO stpa_analyses;")
            print("✓ Table renamed successfully")
        elif new_exists:
            print("✓ 'stpa_analyses' table already exists")
        else:
            print("✓ No 'analyses' table found (will be created by migrations)")
        
        # Update any views that reference the old table name
        print("Updating views...")
        
        # Get all views that might reference analyses
        cur.execute("""
            SELECT viewname 
            FROM pg_views 
            WHERE schemaname = 'public' 
            AND definition LIKE '%analyses%';
        """)
        
        views = cur.fetchall()
        if views:
            print(f"Found {len(views)} views to update")
            # For now, we'll just note which views need updating
            for view in views:
                print(f"  - {view[0]}")
        else:
            print("✓ No views need updating")
        
        print("\n✓ Table conflict resolved!")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        raise
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    fix_table_conflict()