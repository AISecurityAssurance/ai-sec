#!/bin/bash
# Script to run database tests in Docker environment

set -e  # Exit on error

echo "==================================="
echo "Running Database Tests in Container"
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: Must run from apps/backend directory${NC}"
    exit 1
fi

# Function to wait for service
wait_for_service() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}Waiting for $service to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f docker-compose.yml ps | grep -q "$service.*healthy"; then
            echo -e "${GREEN}✓ $service is ready${NC}"
            return 0
        fi
        
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}✗ $service failed to start${NC}"
    return 1
}

# Step 1: Start services
echo -e "\n${YELLOW}Step 1: Starting services...${NC}"
docker-compose -f docker-compose.yml up -d postgres redis

# Step 2: Wait for services to be healthy
echo -e "\n${YELLOW}Step 2: Waiting for services...${NC}"
wait_for_service "sa_postgres"
wait_for_service "sa_redis"

# Step 3: Build backend image if needed
echo -e "\n${YELLOW}Step 3: Building backend image...${NC}"
docker-compose -f docker-compose.dev.yml build backend

# Step 4: Run database setup script
echo -e "\n${YELLOW}Step 4: Setting up database...${NC}"
# Note: Database should already exist from docker-compose, but let's verify
docker-compose -f docker-compose.dev.yml run --rm backend python setup_database.py || true

# Step 5: Run database tests
echo -e "\n${YELLOW}Step 5: Running database tests...${NC}"
docker-compose -f docker-compose.dev.yml run --rm backend python test_database_setup.py

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}==================================="
    echo "✓ All database tests passed!"
    echo "===================================${NC}"
    
    echo -e "\n${YELLOW}You can now:${NC}"
    echo "1. Start the backend API:"
    echo "   docker-compose -f docker-compose.dev.yml up backend"
    echo ""
    echo "2. Access the services:"
    echo "   - API: http://localhost:8000"
    echo "   - pgAdmin: http://localhost:5050 (admin@securityanalyst.local / admin)"
    echo "   - Redis Commander: http://localhost:8081"
    echo ""
    echo "3. Run commands in the container:"
    echo "   docker-compose -f docker-compose.dev.yml exec backend bash"
else
    echo -e "\n${RED}==================================="
    echo "✗ Some database tests failed"
    echo "===================================${NC}"
    echo ""
    echo "Check the logs above for details."
    exit 1
fi