#!/bin/bash

# Security Analyst Platform - Production Setup Script

# Default values
BIND_IP="0.0.0.0"
FRONTEND_PORT="3002"

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
            echo "  --ip IP      Bind to specific IP (default: 0.0.0.0)"
            echo "  --port PORT  Frontend port (default: 3002)"
            echo ""
            echo "Examples:"
            echo "  $0                    # Use defaults"
            echo "  $0 --port 80         # Use port 80"
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

echo "🚀 Security Analyst Platform - Production Setup"
echo "=============================================="
echo ""
echo "Configuration:"
echo "  IP: $BIND_IP"
echo "  Port: $FRONTEND_PORT"

# Export variables for docker-compose
export BIND_IP
export FRONTEND_PORT

# Check for .env file
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << EOF
# API Keys
OPENAI_API_KEY=your-openai-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
GROQ_API_KEY=
GOOGLE_API_KEY=

# Security
SECRET_KEY=$(openssl rand -hex 32)
EOF
    echo "Please edit .env and add your API keys"
    exit 1
fi

# Stop any existing services
echo ""
echo "🛑 Stopping existing services..."
docker compose -f docker-compose.prod.yml down 2>/dev/null || true
docker compose -f docker-compose.test.yml down 2>/dev/null || true

# Build and start services
echo ""
echo "🔨 Building and starting production services..."
echo "   This may take several minutes on first run..."
docker compose -f docker-compose.prod.yml up --build -d

# Wait for services
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 15

# Check service health
echo ""
echo "🏥 Checking service health..."

# Check backend (internal)
if docker compose -f docker-compose.prod.yml exec backend curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running"
else
    echo "⚠️  Backend API is not responding yet. Check logs with: docker compose -f docker-compose.prod.yml logs backend"
fi

# Check frontend
if curl -s http://localhost:${FRONTEND_PORT} > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend is not responding yet. Check logs with: docker compose -f docker-compose.prod.yml logs frontend"
fi

# Display access information
echo ""
echo "🎉 Production setup complete!"
echo ""
echo "Access the application at:"
if [ "$BIND_IP" = "0.0.0.0" ]; then
    echo "  🌐 Frontend: http://<your-server-ip>:${FRONTEND_PORT}"
    echo "  🌐 Also accessible at: http://$(hostname):${FRONTEND_PORT}"
else
    echo "  🌐 Frontend: http://${BIND_IP}:${FRONTEND_PORT}"
fi
echo ""
echo "Useful commands:"
echo "  View logs:    docker compose -f docker-compose.prod.yml logs -f"
echo "  Stop:         docker compose -f docker-compose.prod.yml down"
echo "  Restart:      docker compose -f docker-compose.prod.yml restart"
echo ""
echo "⚠️  Note: This is using nginx to serve the frontend, which should work with any hostname!"
echo ""