# Database Setup Guide

## Prerequisites

1. PostgreSQL 14+ installed and running
2. Python 3.8+ with pip
3. Access to PostgreSQL superuser (usually 'postgres')

## Quick Start

### 1. Install Dependencies

```bash
cd apps/backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` and update:
- Database credentials if different from defaults
- At least one LLM API key (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)
- SECRET_KEY for production

### 3. Create Database

Run the setup script to create the database and user:

```bash
python setup_database.py
```

This will:
- Create the `sa_user` PostgreSQL user
- Create the `security_analyst` database
- Grant necessary privileges

If you get permission errors, you may need to:
```bash
# Option 1: Set superuser password
export POSTGRES_SUPERUSER_PASSWORD=your_postgres_password
python setup_database.py

# Option 2: Use sudo (Linux/Mac)
sudo -u postgres psql -c "CREATE USER sa_user WITH PASSWORD 'sa_password';"
sudo -u postgres psql -c "CREATE DATABASE security_analyst OWNER sa_user;"
```

### 4. Run Migrations and Tests

Run the comprehensive test script:

```bash
python test_database_setup.py
```

This will:
1. Test database connection
2. Run all migrations (creates tables, functions, views)
3. Verify all tables exist
4. Test database functions
5. Insert demo data
6. Verify the data

Expected output:
```
============================================================
DATABASE SETUP AND TESTING
============================================================
1. Testing database connection...
   ✓ Connected to PostgreSQL: PostgreSQL 14.x ...

2. Running migrations...
   ✓ 001_core_stpa_sec_tables.sql completed
   ✓ 002_analysis_tables.sql completed
   ✓ 003_stpa_sec_plus_enhancements.sql completed
   ✓ 004_views_and_analytics.sql completed
   ✓ 005_cve_integration.sql completed

3. Verifying tables...
   ✓ adversaries
   ✓ analysis_results
   ... (all tables listed)

4. Testing database functions...
   ✓ calculate_trust_boundary_risk exists
   ✓ propagate_compromise exists

5. Inserting test data...
   ✓ Test data inserted successfully

6. Verifying test data...
   Systems: 1
     - Autonomous Surveillance Drone System (defense)
   Adversaries: 3
     - Script Kiddie (low)
     - Organized Crime (medium)
     - Nation State (high)
   ...

============================================================
SUMMARY
============================================================
Connection.................................... ✓ PASSED
Migrations................................... ✓ PASSED
Tables....................................... ✓ PASSED
Functions.................................... ✓ PASSED
Test Data.................................... ✓ PASSED
Verification................................. ✓ PASSED
============================================================

✓ All database tests passed! The database is ready to use.
```

## Database Schema Overview

The database includes:

### Core STPA-Sec Tables
- `system_definitions` - Systems being analyzed
- `adversaries` - Threat actors with sophistication levels
- `control_loops` - STPA control structures
- `entities` - System components (controllers, processes, etc.)
- `unsafe_control_actions` - UCAs with temporal context
- `loss_scenarios` - Attack scenarios and impacts

### Analysis Support
- `analysis_sessions` - Track analysis runs
- `analysis_results` - Store LLM outputs
- `stride_analysis` - STRIDE threat mappings
- `framework_mappings` - Cross-framework integration

### Enhanced Features
- `temporal_phases` - Operational modes
- `adversarial_ucas` - Adversary-specific analysis
- `wargaming_sessions` - Red team exercises
- `cve_database` - Vulnerability tracking
- `entity_vulnerabilities` - CVE mappings with context

### Views and Functions
- `system_risk_dashboard` - Executive summary
- `calculate_trust_boundary_risk()` - Risk scoring
- `propagate_compromise()` - Attack path analysis
- `calculate_contextual_risk_score()` - CVE prioritization

## Troubleshooting

### Connection Refused
- Check PostgreSQL is running: `sudo systemctl status postgresql`
- Verify port 5432 is open: `netstat -an | grep 5432`

### Permission Denied
- Ensure PostgreSQL user has correct permissions
- Check pg_hba.conf allows local connections

### Migration Errors
- If tables already exist, the script will skip them
- To reset: `DROP DATABASE security_analyst;` and start over

### Missing Functions
- Functions are created in migration 004
- Check for syntax errors in SQL files

## Next Steps

1. Start the FastAPI backend:
   ```bash
   uvicorn main:app --reload
   ```

2. Test the API:
   ```bash
   curl http://localhost:8000/api/v1/health
   ```

3. Run STPA-Sec analysis using the populated demo data

## Database Management

### Backup
```bash
pg_dump -U sa_user -d security_analyst > backup.sql
```

### Restore
```bash
psql -U sa_user -d security_analyst < backup.sql
```

### Reset Database
```bash
python setup_database.py
python test_database_setup.py
```