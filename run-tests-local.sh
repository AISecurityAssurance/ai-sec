#!/bin/bash

# Run integration tests locally without Docker
set -e

echo "🧪 Security Analyst Integration Tests (Local)"
echo "============================================"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend is running
check_backend() {
    echo -e "${YELLOW}Checking if backend is running...${NC}"
    
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Backend is running${NC}"
    else
        echo -e "${RED}Error: Backend is not running${NC}"
        echo "Please start the backend first with: ./run-backend-local.sh"
        exit 1
    fi
}

# Check if frontend is running
check_frontend() {
    echo -e "${YELLOW}Checking if frontend is running...${NC}"
    
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is running on port 5173${NC}"
        FRONTEND_URL="http://localhost:5173"
    elif curl -s http://localhost:5174 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is running on port 5174${NC}"
        FRONTEND_URL="http://localhost:5174"
    elif curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Frontend is running on port 3000${NC}"
        FRONTEND_URL="http://localhost:3000"
    else
        echo -e "${RED}Error: Frontend is not running${NC}"
        echo "Please start the frontend first with: cd apps/web && npm run dev"
        exit 1
    fi
}

# Configure test models if needed
configure_test_models() {
    echo -e "\n${YELLOW}Checking model configuration...${NC}"
    
    # Check if any models are configured
    MODELS_RESPONSE=$(curl -s http://localhost:8000/api/v1/settings/models)
    
    if [ -n "${OLLAMA_ENDPOINT}" ]; then
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
        # Check if any models are already configured
        if echo "$MODELS_RESPONSE" | grep -q '"provider"'; then
            echo -e "${GREEN}✓ Found existing model configuration${NC}"
        else
            echo -e "${YELLOW}⚠ No models configured, tests will use mock LLM responses${NC}"
        fi
    fi
}

# Install test dependencies
install_test_deps() {
    echo -e "\n${YELLOW}Installing test dependencies...${NC}"
    
    cd integration-tests
    if [ ! -d "node_modules" ]; then
        npm install
    fi
    cd ..
    
    echo -e "${GREEN}✓ Test dependencies ready${NC}"
}

# Run tests
run_tests() {
    echo -e "\n${YELLOW}Running integration tests...${NC}"
    
    cd integration-tests
    
    # Set test environment variables
    export BACKEND_URL="http://localhost:8000"
    export FRONTEND_URL="${FRONTEND_URL}"
    export HEADLESS="false"  # Show browser for local testing
    
    # Run the tests
    npm test
    
    if [ $? -eq 0 ]; then
        echo -e "\n${GREEN}✓ All integration tests passed!${NC}"
    else
        echo -e "\n${RED}✗ Some integration tests failed${NC}"
        exit 1
    fi
}

# Simple unit tests without Playwright
run_api_tests() {
    echo -e "\n${YELLOW}Running API tests...${NC}"
    
    # Test health endpoint
    echo -n "Testing health endpoint... "
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
    fi
    
    # Test WebSocket connection
    echo -n "Testing WebSocket endpoint... "
    # This is a simple check - real WebSocket test needs a client
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ws/test-user | grep -q "426"; then
        echo -e "${GREEN}✓${NC} (Upgrade required - correct response)"
    else
        echo -e "${RED}✗${NC}"
    fi
    
    # Test analysis endpoint
    echo -n "Testing analysis endpoint... "
    RESPONSE=$(curl -s -X POST http://localhost:8000/api/v1/analysis/stpa-sec \
        -H "Content-Type: application/json" \
        -d '{
            "user_id": "test-user",
            "system_description": "Test system",
            "components": ["Component A", "Component B"],
            "data_flows": []
        }')
    
    if echo "$RESPONSE" | grep -q "analysis_id"; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo "Response: $RESPONSE"
    fi
}

# Main execution
main() {
    check_backend
    check_frontend
    configure_test_models
    
    # Check if Playwright is available
    if command -v npx &> /dev/null && [ -f "integration-tests/package.json" ]; then
        install_test_deps
        run_tests
    else
        echo -e "\n${YELLOW}Playwright not available, running basic API tests...${NC}"
        run_api_tests
    fi
}

# Run main function
main