#!/bin/bash

# Run a single integration test for faster debugging
set -e

TEST_FILE=${1:-"tests/02-create-analysis.spec.ts"}
TEST_NAME=${2:-""}

echo "🧪 Running Single Integration Test"
echo "================================"
echo "Test file: $TEST_FILE"
echo ""

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    echo "Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
fi

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if services are running
if ! docker ps | grep -q prototype1-backend-1; then
    echo -e "${YELLOW}Starting services...${NC}"
    docker compose -f docker-compose.test.yml up -d --build
    echo "Waiting for services to start..."
    sleep 10
fi

# Configure test models if API keys exist
if [ -n "${OPENAI_API_KEY}" ]; then
    echo -e "${GREEN}✓ Configuring OpenAI for testing${NC}"
    curl -X POST http://localhost:8000/api/v1/settings/models/openai \
        -H "Content-Type: application/json" \
        -d '{
            "provider": "openai",
            "api_key": "'${OPENAI_API_KEY}'",
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 4096,
            "auth_method": "api-key",
            "is_enabled": true
        }' > /dev/null 2>&1
    
    curl -X POST http://localhost:8000/api/v1/settings/active-provider \
        -H "Content-Type: application/json" \
        -d '{"provider": "openai"}' > /dev/null 2>&1
fi

# Run the specific test
cd integration-tests

if [ -n "$TEST_NAME" ]; then
    echo -e "\n${YELLOW}Running specific test: $TEST_NAME${NC}"
    npx playwright test "$TEST_FILE" -g "$TEST_NAME" --config=playwright.config.fast.ts
else
    echo -e "\n${YELLOW}Running all tests in: $TEST_FILE${NC}"
    npx playwright test "$TEST_FILE" --config=playwright.config.fast.ts
fi

# Show backend logs if test failed
if [ $? -ne 0 ]; then
    echo -e "\n${RED}Test failed. Showing backend logs:${NC}"
    docker logs prototype1-backend-1 --tail 50
fi