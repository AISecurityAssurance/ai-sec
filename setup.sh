#!/bin/bash

# Security Analyst Platform - Setup Script

# Default values
BIND_IP="localhost"
FRONTEND_PORT="3000"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --ip)
            BIND_IP="$2"
            shift 2
            ;;
        --port)
            FRONTEND_PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --ip IP      Bind to specific IP (default: localhost)"
            echo "  --port PORT  Frontend port (default: 3000)"
            echo ""
            echo "Examples:"
            echo "  $0                    # Use defaults"
            echo "  $0 --ip 0.0.0.0      # Bind to all interfaces"
            echo "  $0 --port 3002       # Use port 3002"
            echo "  $0 --ip 0.0.0.0 --port 3002"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

echo "🚀 Security Analyst Platform Setup"
echo "=================================="
echo ""
echo "Configuration:"
echo "  IP: $BIND_IP"
echo "  Port: $FRONTEND_PORT"

# Check for required tools
check_requirement() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is required but not installed."
        echo "   Please install $1 and try again."
        exit 1
    fi
    echo "✅ $1 found"
}

echo ""
echo "Checking requirements..."
check_requirement docker
check_requirement git

# Check if .env file exists
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cat > .env << EOF
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Anthropic API Configuration (optional)
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Groq API Configuration (optional)
GROQ_API_KEY=

# Google API Configuration (optional)
GOOGLE_API_KEY=
EOF
    echo "⚠️  Please edit .env file and add your API keys"
    echo "   At minimum, you need either OPENAI_API_KEY or ANTHROPIC_API_KEY"
    echo ""
    read -p "Press Enter after adding your API keys to continue..."
fi

# Pull latest changes
echo ""
echo "📥 Pulling latest changes..."
git pull

# Create temporary docker-compose override for custom IP/port
if [ "$BIND_IP" != "localhost" ] || [ "$FRONTEND_PORT" != "3000" ]; then
    echo ""
    echo "📝 Creating docker-compose override for custom IP/port..."
    cat > docker-compose.override.yml << EOF
services:
  frontend:
    ports:
      - "${BIND_IP}:${FRONTEND_PORT}:5173"
  backend:
    ports:
      - "${BIND_IP}:8000:8000"
  postgres:
    ports:
      - "${BIND_IP}:5433:5432"
  redis:
    ports:
      - "${BIND_IP}:6380:6379"
EOF
fi

# Build and start services
echo ""
echo "🔨 Building and starting services..."
echo "   This may take a few minutes on first run..."
docker compose -f docker-compose.test.yml up --build -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo ""
echo "🏥 Checking service health..."

# Determine the URL to check
if [ "$BIND_IP" = "0.0.0.0" ]; then
    CHECK_IP="localhost"
else
    CHECK_IP="$BIND_IP"
fi

# Check backend
if curl -s http://${CHECK_IP}:8000/health > /dev/null; then
    echo "✅ Backend API is running"
else
    echo "⚠️  Backend API is not responding yet. Check logs with: docker compose -f docker-compose.test.yml logs backend"
fi

# Check frontend
if curl -s http://${CHECK_IP}:${FRONTEND_PORT} > /dev/null; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend is not responding yet. Check logs with: docker compose -f docker-compose.test.yml logs frontend"
fi

# Display access information
echo ""
echo "🎉 Setup complete!"
echo ""
echo "Access the application at:"
if [ "$BIND_IP" = "0.0.0.0" ]; then
    echo "  🌐 Frontend: http://<your-server-ip>:${FRONTEND_PORT}"
    echo "  🔧 Backend API: http://<your-server-ip>:8000"
    echo "  📚 API Docs: http://<your-server-ip>:8000/docs"
else
    echo "  🌐 Frontend: http://${BIND_IP}:${FRONTEND_PORT}"
    echo "  🔧 Backend API: http://${BIND_IP}:8000"
    echo "  📚 API Docs: http://${BIND_IP}:8000/docs"
fi
echo ""
echo "Useful commands:"
echo "  View logs:    docker compose -f docker-compose.test.yml logs -f"
echo "  Stop:         docker compose -f docker-compose.test.yml down"
echo "  Restart:      docker compose -f docker-compose.test.yml restart"
echo "  Clean start:  docker compose -f docker-compose.test.yml down -v && ./setup.sh"
if [ -f docker-compose.override.yml ]; then
    echo "  Remove override: rm docker-compose.override.yml"
fi
echo ""
echo "To run integration tests:"
echo "  cd integration-tests && npm test"
echo ""