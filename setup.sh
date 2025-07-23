#!/bin/bash

# Security Analyst Platform - Setup Script
echo "🚀 Security Analyst Platform Setup"
echo "=================================="

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

# Check backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is running"
else
    echo "⚠️  Backend API is not responding yet. Check logs with: docker compose -f docker-compose.test.yml logs backend"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend is not responding yet. Check logs with: docker compose -f docker-compose.test.yml logs frontend"
fi

# Display access information
echo ""
echo "🎉 Setup complete!"
echo ""
echo "Access the application at:"
echo "  🌐 Frontend: http://localhost:3000"
echo "  🔧 Backend API: http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Useful commands:"
echo "  View logs:    docker compose -f docker-compose.test.yml logs -f"
echo "  Stop:         docker compose -f docker-compose.test.yml down"
echo "  Restart:      docker compose -f docker-compose.test.yml restart"
echo "  Clean start:  docker compose -f docker-compose.test.yml down -v && ./setup.sh"
echo ""
echo "To run integration tests:"
echo "  cd integration-tests && npm test"
echo ""