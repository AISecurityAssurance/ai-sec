#!/bin/bash

echo "🔍 Checking Remote Access Issues"
echo "================================"

# Check if containers are running
echo ""
echo "1️⃣ Container Status:"
docker compose -f docker-compose.prod.yml ps

# Check nginx logs for errors
echo ""
echo "2️⃣ Recent Frontend Errors:"
docker compose -f docker-compose.prod.yml logs frontend --tail 20 | grep -E "error|Error|failed|Failed" || echo "No errors found"

# Check backend connectivity from frontend container
echo ""
echo "3️⃣ Backend Connectivity from Frontend Container:"
docker compose -f docker-compose.prod.yml exec frontend wget -O- http://backend:8000/health 2>&1 | head -5 || echo "Failed to connect to backend from frontend container"

# Check listening ports
echo ""
echo "4️⃣ Port 3002 Status:"
sudo netstat -tlnp | grep 3002 || ss -tlnp | grep 3002 || echo "Need sudo to check port binding"

# Check firewall
echo ""
echo "5️⃣ Firewall Status:"
if command -v ufw &> /dev/null; then
    sudo ufw status | grep 3002 || echo "Port 3002 not explicitly allowed in UFW"
fi

# Test from inside the frontend container
echo ""
echo "6️⃣ Testing Frontend Response:"
curl -s -I http://localhost:3002 | head -5

echo ""
echo "7️⃣ Testing API through Nginx:"
curl -s http://localhost:3002/api/health | jq . || echo "API not accessible through nginx"

echo ""
echo "✅ If all checks pass but remote access fails, the issue might be:"
echo "   - Ubuntu firewall blocking incoming connections on port 3002"
echo "   - Cloud provider security group/firewall rules"
echo "   - Network routing between machines"
echo ""
echo "🔧 To fix Ubuntu firewall (if using UFW):"
echo "   sudo ufw allow 3002/tcp"
echo "   sudo ufw reload"