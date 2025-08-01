# Step 2 Docker Environment Fix

## Issue
When running Step 2 analysis in Docker with `./ai-sec analyze --use-database <db> --step 2`, the error "column 'identifier' does not exist" persists even though:
1. The CLI shows the identifier column exists when checking schema
2. Manual checks from the host confirm the column exists
3. Migrations appear to run successfully

## Root Cause Analysis
The issue appears to be related to:
1. Database connection isolation between the CLI and agent processes
2. Possible transaction boundaries preventing schema changes from being visible
3. Docker container database host resolution differences

## Solutions Implemented

### 1. Migration 020_step2_ensure_identifier.sql
- Uses ALTER TABLE ADD COLUMN IF NOT EXISTS to safely add identifier columns
- Updates any NULL values with generated identifiers
- More graceful than dropping and recreating tables

### 2. Enhanced CLI Migration Check (cli.py)
- Improved detection of missing identifier column
- Runs appropriate migration when column is missing
- Better error handling and logging

### 3. Agent Debug Logging
- Added schema checking in ControlStructureAnalystAgent
- Logs actual columns seen by the agent
- Helps identify connection/transaction issues

## Temporary Workaround
If the issue persists, manually run the migration from within the Docker container:

```bash
# Connect to the Docker container
docker exec -it sa_backend bash

# Run Python to execute migration
python3 -c "
import asyncio
import asyncpg

async def fix_db():
    db_name = 'stpa_analysis_20250730_200742'  # Your database name
    conn = await asyncpg.connect(f'postgresql://sa_user:sa_password@postgres:5432/{db_name}')
    
    # Run the ensure identifier migration
    with open('migrations/020_step2_ensure_identifier.sql', 'r') as f:
        await conn.execute(f.read())
        
    print('Migration completed!')
    await conn.close()

asyncio.run(fix_db())
"
```

## Long-term Solution
The issue suggests we need to:
1. Ensure all database operations use the same connection pool
2. Review transaction boundaries in Step 2 coordinator
3. Consider using a connection wrapper that ensures schema consistency

## Next Steps
1. Test the 020 migration with the problematic database
2. If issue persists, implement connection pooling in Step2Coordinator
3. Add retry logic for schema-related errors