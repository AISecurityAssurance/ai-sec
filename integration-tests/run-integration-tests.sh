#!/bin/bash

# Integration test runner for Security Analyst Platform
set -e

echo "🧪 Security Analyst Integration Tests"
echo "===================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if required environment variables are set
check_env_vars() {
    echo -e "${YELLOW}Checking environment variables...${NC}"
    
    required_vars=("OPENAI_API_KEY" "ANTHROPIC_API_KEY")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=($var)
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo -e "${RED}Error: Missing required environment variables:${NC}"
        printf '%s\n' "${missing_vars[@]}"
        echo "Please set these in your .env file or export them"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Environment variables OK${NC}"
}

# Start services
start_services() {
    echo -e "\n${YELLOW}Starting services...${NC}"
    
    # Stop any existing services
    docker-compose -f docker-compose.test.yml down -v
    
    # Start services
    docker-compose -f docker-compose.test.yml up -d --build
    
    # Wait for services to be ready
    echo "Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if docker-compose -f docker-compose.test.yml ps | grep -q "Exit"; then
        echo -e "${RED}Error: Some services failed to start${NC}"
        docker-compose -f docker-compose.test.yml logs
        exit 1
    fi
    
    echo -e "${GREEN}✓ Services started${NC}"
}

# Wait for backend to be ready
wait_for_backend() {
    echo -e "\n${YELLOW}Waiting for backend API...${NC}"
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend API is ready${NC}"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "Attempt $attempt/$max_attempts..."
        sleep 2
    done
    
    echo -e "${RED}Error: Backend API failed to start${NC}"
    docker-compose -f docker-compose.test.yml logs backend
    exit 1
}

# Wait for frontend to be ready
wait_for_frontend() {
    echo -e "\n${YELLOW}Waiting for frontend...${NC}"
    
    max_attempts=30
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Frontend is ready${NC}"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "Attempt $attempt/$max_attempts..."
        sleep 2
    done
    
    echo -e "${RED}Error: Frontend failed to start${NC}"
    docker-compose -f docker-compose.test.yml logs frontend
    exit 1
}

# Run integration tests
run_tests() {
    echo -e "\n${YELLOW}Running integration tests...${NC}"
    
    # Run the test suite
    cd integration-tests
    npm test
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ All integration tests passed!${NC}"
    else
        echo -e "${RED}✗ Some integration tests failed${NC}"
        exit 1
    fi
}

# Cleanup
cleanup() {
    echo -e "\n${YELLOW}Cleaning up...${NC}"
    docker-compose -f docker-compose.test.yml down -v
    echo -e "${GREEN}✓ Cleanup complete${NC}"
}

# Main execution
main() {
    # Trap to ensure cleanup on exit
    trap cleanup EXIT
    
    check_env_vars
    start_services
    wait_for_backend
    wait_for_frontend
    run_tests
}

# Run main function
main