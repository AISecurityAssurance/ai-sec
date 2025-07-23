#\!/bin/bash
set -e

echo "🔄 Rebuilding frontend with latest changes..."

# Stop all containers
docker compose -f docker-compose.test.yml down

# Remove the frontend image to force rebuild
docker rmi prototype1-frontend 2>/dev/null || true

# Rebuild everything
docker compose -f docker-compose.test.yml build --no-cache frontend backend

# Start services
docker compose -f docker-compose.test.yml up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 15

# Check if frontend is running
echo "🔍 Checking frontend..."
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend is running" || echo "❌ Frontend not responding"

# Check if backend is running  
echo "🔍 Checking backend..."
curl -s http://localhost:8000/api/health > /dev/null && echo "✅ Backend is running" || echo "❌ Backend not responding"

# Run the test
if [ -n "$1" ]; then
    ./integration-tests/run-single-test.sh "$1" "$2"
else
    echo "Usage: $0 <test-file> [test-name]"
    echo "Example: $0 tests/02-create-analysis.spec.ts"
fi
