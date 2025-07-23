#!/bin/bash

echo "🔄 Restarting production services..."

# Check if production services are running
if docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "📦 Found running production services"
    docker compose -f docker-compose.prod.yml restart
    echo "✅ Services restarted"
else
    echo "⚠️  No production services running. Starting fresh..."
    docker compose -f docker-compose.prod.yml up -d
    echo "✅ Services started"
fi

echo ""
echo "💡 Check status with: ./debug-prod.sh"
echo "💡 View logs with: docker compose -f docker-compose.prod.yml logs -f"