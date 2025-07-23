#!/bin/bash

echo "🔍 Docker Network Debugging Script"
echo "=================================="
echo ""

# Check if running with sufficient privileges for some commands
if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Some commands may require sudo. Run with: sudo ./debug.sh"
    echo ""
fi

# 1. Check Docker containers and their port mappings
echo "📦 Docker Container Status:"
echo "-------------------------"
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "(NAMES|3002|8000)" || echo "No containers found with relevant ports"
echo ""

# 2. Check what's actually listening on the ports
echo "🔌 Network Bindings (what's listening):"
echo "--------------------------------------"
if command -v ss &> /dev/null; then
    echo "Port 3002:"
    ss -tlnp | grep :3002 || echo "Nothing listening on port 3002"
    echo "Port 8000:"
    ss -tlnp | grep :8000 || echo "Nothing listening on port 8000"
elif command -v netstat &> /dev/null; then
    echo "Port 3002:"
    netstat -tlnp | grep :3002 || echo "Nothing listening on port 3002"
    echo "Port 8000:"
    netstat -tlnp | grep :8000 || echo "Nothing listening on port 8000"
else
    echo "Neither ss nor netstat found. Install net-tools package."
fi
echo ""

# 3. Check UFW firewall status
echo "🔥 Firewall Status (UFW):"
echo "------------------------"
if command -v ufw &> /dev/null; then
    sudo ufw status verbose | grep -E "(Status:|3002|8000|ALLOW)" || echo "UFW not configured or ports not allowed"
else
    echo "UFW not installed"
fi
echo ""

# 4. Check iptables rules (Docker manages its own)
echo "🔥 Docker IPTables Rules:"
echo "------------------------"
sudo iptables -L DOCKER -n 2>/dev/null | grep -E "(3002|8000)" || echo "No Docker iptables rules found for these ports"
echo ""

# 5. Check if docker-compose.override.yml exists
echo "📄 Docker Compose Override:"
echo "--------------------------"
if [ -f docker-compose.override.yml ]; then
    echo "Override file exists with content:"
    cat docker-compose.override.yml
else
    echo "No docker-compose.override.yml found"
fi
echo ""

# 6. Test port accessibility
echo "🧪 Port Accessibility Tests:"
echo "---------------------------"
echo "Testing localhost:3002..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:3002 || echo "Failed to connect"
echo "Testing 0.0.0.0:3002..."
curl -s -o /dev/null -w "Status: %{http_code}\n" http://0.0.0.0:3002 || echo "Failed to connect"
echo ""

# 7. Show network interfaces
echo "🌐 Network Interfaces:"
echo "---------------------"
ip addr show | grep -E "(^[0-9]+:|inet )" | grep -v "inet6"
echo ""

# 8. Check Docker daemon configuration
echo "⚙️  Docker Daemon Config:"
echo "-----------------------"
if [ -f /etc/docker/daemon.json ]; then
    cat /etc/docker/daemon.json
else
    echo "No custom daemon.json found"
fi
echo ""

# 9. Show actual docker-compose command being used
echo "📋 Docker Compose Files in Use:"
echo "------------------------------"
ls -la docker-compose*.yml 2>/dev/null || echo "No docker-compose files found in current directory"
echo ""

# 10. Diagnosis and recommendations
echo "🩺 Diagnosis:"
echo "============"
echo ""

# Check if container is running
if docker ps | grep -q "3002"; then
    echo "✅ Container is running with port 3002"
    
    # Check if bound to 0.0.0.0
    if ss -tlnp 2>/dev/null | grep -q "0.0.0.0:3002" || netstat -tlnp 2>/dev/null | grep -q "0.0.0.0:3002"; then
        echo "✅ Port 3002 is bound to all interfaces (0.0.0.0)"
        
        # Check firewall
        if sudo ufw status 2>/dev/null | grep -q "3002.*ALLOW"; then
            echo "✅ UFW firewall allows port 3002"
        else
            echo "❌ UFW firewall may be blocking port 3002"
            echo "   Fix: sudo ufw allow 3002/tcp"
        fi
    else
        echo "❌ Port 3002 appears to be bound to localhost only"
        echo "   The container needs to bind to 0.0.0.0:3002, not 127.0.0.1:3002"
    fi
else
    echo "❌ No container found using port 3002"
fi

echo ""
echo "💡 Common Solutions:"
echo "==================="
echo "1. If firewall is blocking:"
echo "   sudo ufw allow 3002/tcp"
echo "   sudo ufw allow 8000/tcp"
echo ""
echo "2. If container is bound to localhost only:"
echo "   Make sure docker-compose.override.yml has:"
echo "   - \"0.0.0.0:3002:5173\""
echo ""
echo "3. Restart services after changes:"
echo "   ./stop.sh && ./setup.sh --ip 0.0.0.0 --port 3002"
echo ""