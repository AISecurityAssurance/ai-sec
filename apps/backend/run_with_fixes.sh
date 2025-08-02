#!/bin/bash
# Run Step 2 analysis with fixes applied

cd /Users/loripickering/Projects/prototype1

# Start the containers
docker-compose up -d

# Wait for backend container to be ready
sleep 2

# Copy and run the fix script
docker cp apps/backend/fix_step2_mock.sh sa_backend:/tmp/
docker exec sa_backend bash /tmp/fix_step2_mock.sh

# Now run the analysis
./apps/backend/ai-sec analyze --config example_systems/sd-wan/config.yaml --use-database stpa_analysis_20250731_180007 --step 2 --save-prompt