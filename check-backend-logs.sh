#!/bin/bash

# Quick script to check backend logs and status

echo "🔍 Checking backend status..."
echo "=============================="

# Check if backend container is running
if docker ps | grep -q "prototype1-backend-1"; then
    echo "✓ Backend container is running"
else
    echo "✗ Backend container is not running"
fi

echo -e "\n📋 Backend logs (last 50 lines):"
echo "--------------------------------"
docker logs prototype1-backend-1 --tail 50

echo -e "\n🌐 Testing backend endpoints:"
echo "-----------------------------"

# Test health endpoint
echo -n "Health endpoint: "
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Responding"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Invalid JSON response"
else
    echo "✗ Not responding"
fi

# Test root endpoint
echo -n "Root endpoint: "
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "✓ Responding"
else
    echo "✗ Not responding"
fi

# Check if migrations are blocking
echo -e "\n🗄️  Database status:"
echo "-------------------"
docker exec prototype1-backend-1 alembic current 2>/dev/null || echo "Cannot check migration status"