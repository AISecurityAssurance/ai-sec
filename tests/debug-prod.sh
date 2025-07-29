#!/bin/bash

echo "🔍 Debugging Production Setup"
echo "============================"
echo ""

# Check running containers
echo "📦 Running containers:"
docker compose -f docker-compose.prod.yml ps
echo ""

# Check frontend logs
echo "📝 Frontend logs (last 50 lines):"
docker compose -f docker-compose.prod.yml logs --tail=50 frontend
echo ""

# Check backend logs
echo "📝 Backend logs (last 30 lines):"
docker compose -f docker-compose.prod.yml logs --tail=30 backend
echo ""

# Check if services are healthy
echo "🏥 Service health checks:"
echo -n "Frontend (nginx): "
if curl -s -o /dev/null -w "%{http_code}" http://localhost:${FRONTEND_PORT:-3002} | grep -q "200\|304"; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

echo -n "Backend API: "
if docker compose -f docker-compose.prod.yml exec backend curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not responding"
fi

echo ""
echo "💡 To see live logs: docker compose -f docker-compose.prod.yml logs -f"
echo "💡 To restart services: docker compose -f docker-compose.prod.yml restart"