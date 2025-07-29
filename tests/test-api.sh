#!/bin/bash

echo "🧪 Testing API connectivity"
echo "=========================="
echo ""

# Test from inside the frontend container
echo "1. Testing from inside frontend container:"
docker compose -f docker-compose.prod.yml exec frontend sh -c "
  echo '   Checking backend connectivity...'
  wget -qO- http://backend:8000/health || echo '   ❌ Cannot reach backend from frontend container'
"

echo ""
echo "2. Testing from host:"
echo "   Checking frontend nginx..."
curl -s http://localhost:${1:-3002}/ > /dev/null && echo "   ✅ Frontend nginx is responding" || echo "   ❌ Frontend nginx not responding"

echo ""
echo "3. Testing API proxy through nginx:"
curl -s http://localhost:${1:-3002}/api/v1/health || echo "   ❌ API proxy not working"

echo ""
echo "4. Checking nginx logs for API requests:"
docker compose -f docker-compose.prod.yml logs --tail=20 frontend | grep "/api" || echo "   No API requests found in logs"

echo ""
echo "💡 If API proxy is not working, check nginx configuration"