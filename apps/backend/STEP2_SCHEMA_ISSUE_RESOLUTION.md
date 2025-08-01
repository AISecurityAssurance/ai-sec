# Step 2 Schema Issue Resolution

## Problem Summary
The Step 2 implementation was encountering "column 'identifier' does not exist" errors when running against older databases created before the current schema was established.

## Root Causes
1. **Old Step 1 Schema**: Databases created before the current implementation lack:
   - `identifier` columns in losses, hazards, and system_components tables
   - `analysis_id` columns to link Step 1 data to specific analyses
   - Proper foreign key relationships

2. **Docker Environment**: The schema appears correct when checked from the host but fails in Docker due to connection/transaction isolation issues.

## Solutions Implemented

### 1. Database Compatibility Layer (`db_compat.py`)
- Checks for column existence before INSERT operations
- Falls back to old schema format when needed
- Handles both new and old database schemas

### 2. Step 1 Data Loading Fixes (`base_step2.py`)
- Added schema detection for losses and hazards tables
- Generates synthetic identifiers for old schema
- Maps old properties JSON to new column format

### 3. Migration Improvements
- Created migration 020_step2_ensure_identifier.sql
- Added automatic migration running in CLI
- Force rebuild option for broken schemas

## Recommendation
**Use fresh databases created with the current schema for Step 2 analysis.**

Old databases (before 2025-07-31) have incompatible schemas that require extensive compatibility layers. While we've implemented workarounds, it's more reliable to:

1. Run fresh Step 1 analysis to create a new database
2. Use the `--step 2` flag with the new database

## Example Commands
```bash
# Create fresh Step 1 analysis
./ai-sec analyze --config example_systems/sd-wan/config.yaml

# Note the database name from output, then run Step 2
./ai-sec analyze --config example_systems/sd-wan/config.yaml \
  --use-database stpa_analysis_20250731_XXXXXX --step 2
```

## Technical Details
The current schema expects:
- Step 1 tables with `identifier` and `analysis_id` columns
- Proper foreign key relationships
- Step 2 tables created by migrations 016-020

Older databases lack these requirements and would need extensive migrations to upgrade.