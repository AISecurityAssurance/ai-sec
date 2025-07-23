#!/bin/bash

# Run backend locally for testing without Docker
set -e

echo "🚀 Starting Security Analyst Backend Locally"
echo "==========================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python
check_python() {
    echo -e "${YELLOW}Checking Python installation...${NC}"
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
        echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
    else
        echo -e "${RED}Error: Python 3 is required${NC}"
        exit 1
    fi
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "apps/backend/venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        cd apps/backend
        python3 -m venv venv
        cd ../..
    fi
    echo -e "${GREEN}✓ Virtual environment ready${NC}"
}

# Install dependencies
install_deps() {
    echo -e "\n${YELLOW}Installing dependencies...${NC}"
    cd apps/backend
    source venv/bin/activate
    pip install -r requirements.txt
    cd ../..
    echo -e "${GREEN}✓ Dependencies installed${NC}"
}

# Set up environment
setup_env() {
    echo -e "\n${YELLOW}Setting up environment...${NC}"
    
    # Create .env file if it doesn't exist
    if [ ! -f "apps/backend/.env" ]; then
        cat > apps/backend/.env << EOF
# Security Analyst Backend Configuration
SECRET_KEY=test-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=True

# Database Configuration (using SQLite for local testing)
DATABASE_URL=sqlite+aiosqlite:///./security_analyst.db

# Model Configuration (Optional - can configure via UI)
# OLLAMA_ENDPOINT=http://localhost:11434
# OLLAMA_MODEL=mistral:instruct

# CORS Origins
CORS_ORIGINS=["http://localhost:5173","http://localhost:5174","http://localhost:3000"]
EOF
        echo -e "${GREEN}✓ Created .env file${NC}"
    else
        echo -e "${GREEN}✓ Using existing .env file${NC}"
    fi
}

# Run migrations
run_migrations() {
    echo -e "\n${YELLOW}Running database migrations...${NC}"
    cd apps/backend
    source venv/bin/activate
    
    # Run alembic migrations if available
    if [ -f "alembic.ini" ]; then
        alembic upgrade head
    else
        echo -e "${YELLOW}No migrations found, database will be created on startup${NC}"
    fi
    
    cd ../..
}

# Start backend
start_backend() {
    echo -e "\n${YELLOW}Starting backend server...${NC}"
    echo -e "${GREEN}Backend will be available at: http://localhost:8000${NC}"
    echo -e "${GREEN}API docs available at: http://localhost:8000/docs${NC}"
    echo -e "${GREEN}WebSocket endpoint: ws://localhost:8000/ws/{user_id}${NC}"
    echo -e "\n${YELLOW}Press Ctrl+C to stop the server${NC}\n"
    
    cd apps/backend
    source venv/bin/activate
    
    # Set Ollama endpoint if available
    if [ -n "${OLLAMA_ENDPOINT}" ]; then
        export OLLAMA_ENDPOINT
        echo -e "${GREEN}✓ Ollama endpoint set to: $OLLAMA_ENDPOINT${NC}"
    fi
    
    # Run the backend
    python main.py
}

# Main execution
main() {
    check_python
    check_venv
    install_deps
    setup_env
    run_migrations
    start_backend
}

# Run main function
main