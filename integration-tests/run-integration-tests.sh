#!/bin/bash

# Integration test runner for Security Analyst Platform
set -e

echo "🧪 Security Analyst Integration Tests"
echo "===================================="

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

# Determine docker compose command
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
elif docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
else
    echo -e "${RED}Error: Neither 'docker-compose' nor 'docker compose' found${NC}"
    exit 1
fi

# Check if required environment variables are set
check_env_vars() {
    echo -e "${YELLOW}Checking test configuration...${NC}"
    
    # Check if we have any LLM configuration (env vars or will use test config)
    if [ -n "${OLLAMA_ENDPOINT}" ] || [ -n "${ANTHROPIC_API_KEY}" ] || [ -n "${OPENAI_API_KEY}" ]; then
        echo -e "${GREEN}✓ Found LLM configuration in environment${NC}"
    else
        echo -e "${YELLOW}⚠ No LLM configuration in environment, will use mock responses for testing${NC}"
    fi
}

# Start services
start_services() {
    echo -e "\n${YELLOW}Starting services...${NC}"
    
    # Stop any existing services
    $DOCKER_COMPOSE -f docker-compose.test.yml down -v
    
    # Start services
    $DOCKER_COMPOSE -f docker-compose.test.yml up -d --build
    
    # Wait for services to be ready
    echo "Waiting for services to start..."
    sleep 10
    
    # Check if services are running
    if $DOCKER_COMPOSE -f docker-compose.test.yml ps | grep -q "Exit"; then
        echo -e "${RED}Error: Some services failed to start${NC}"
        $DOCKER_COMPOSE -f docker-compose.test.yml logs
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
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✓ Backend API is ready${NC}"
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "Attempt $attempt/$max_attempts..."
        sleep 2
    done
    
    echo -e "${RED}Error: Backend API failed to start${NC}"
    $DOCKER_COMPOSE -f docker-compose.test.yml logs backend
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
    $DOCKER_COMPOSE -f docker-compose.test.yml logs frontend
    exit 1
}

# Configure test models if needed
configure_test_models() {
    echo -e "\n${YELLOW}Configuring test models...${NC}"
    
    # Debug: Show which API keys are available
    if [ -n "${OPENAI_API_KEY}" ]; then
        echo -e "${GREEN}✓ OpenAI API key found${NC}"
    fi
    if [ -n "${ANTHROPIC_API_KEY}" ]; then
        echo -e "${GREEN}✓ Anthropic API key found${NC}"
    fi
    if [ -n "${OLLAMA_ENDPOINT}" ]; then
        echo -e "${GREEN}✓ Ollama endpoint found${NC}"
    fi
    
    # Check for OpenAI API key
    if [ -n "${OPENAI_API_KEY}" ]; then
        echo "Configuring OpenAI for testing..."
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
        
        # Set OpenAI as active provider
        curl -X POST http://localhost:8000/api/v1/settings/active-provider \
            -H "Content-Type: application/json" \
            -d '{"provider": "openai"}' > /dev/null 2>&1
        
        echo -e "${GREEN}✓ OpenAI configured for testing${NC}"
        
    # Check for Anthropic API key
    elif [ -n "${ANTHROPIC_API_KEY}" ]; then
        echo "Configuring Anthropic for testing..."
        curl -X POST http://localhost:8000/api/v1/settings/models/anthropic \
            -H "Content-Type: application/json" \
            -d '{
                "provider": "anthropic",
                "api_key": "'${ANTHROPIC_API_KEY}'",
                "model": "claude-3-haiku-20240307",
                "temperature": 0.7,
                "max_tokens": 4096,
                "auth_method": "api-key",
                "is_enabled": true
            }' > /dev/null 2>&1
        
        # Set Anthropic as active provider
        curl -X POST http://localhost:8000/api/v1/settings/active-provider \
            -H "Content-Type: application/json" \
            -d '{"provider": "anthropic"}' > /dev/null 2>&1
        
        echo -e "${GREEN}✓ Anthropic configured for testing${NC}"
        
    # Check for Ollama endpoint
    elif [ -n "${OLLAMA_ENDPOINT}" ]; then
        echo "Configuring Ollama for testing..."
        curl -X POST http://localhost:8000/api/v1/settings/models/ollama \
            -H "Content-Type: application/json" \
            -d '{
                "provider": "ollama",
                "api_endpoint": "'${OLLAMA_ENDPOINT}'",
                "model": "mistral:instruct",
                "temperature": 0.7,
                "max_tokens": 4096,
                "auth_method": "none",
                "is_enabled": true
            }' > /dev/null 2>&1
        
        # Set Ollama as active provider
        curl -X POST http://localhost:8000/api/v1/settings/active-provider \
            -H "Content-Type: application/json" \
            -d '{"provider": "ollama"}' > /dev/null 2>&1
        
        echo -e "${GREEN}✓ Ollama configured for testing${NC}"
    else
        echo -e "${YELLOW}⚠ No models configured, tests will use mock LLM responses${NC}"
    fi
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
    $DOCKER_COMPOSE -f docker-compose.test.yml down -v
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
    configure_test_models
    run_tests
}

# Run main function
main