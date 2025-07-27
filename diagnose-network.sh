#!/bin/bash

echo "🔍 Network Diagnostics for Security Analyst Platform"
echo "===================================================="
echo ""

# Get IP addresses
echo "📍 Network Interfaces:"
if command -v ip &> /dev/null; then
    ip addr show | grep -E "^[0-9]+:|inet " | grep -v "127.0.0.1"
else
    ifconfig | grep -E "inet|UP" | grep -v "127.0.0.1"
fi

echo ""
echo "🐳 Docker Container Ports:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "🔌 Listening Ports:"
if command -v ss &> /dev/null; then
    ss -tlnp | grep 3002 2>/dev/null || sudo ss -tlnp | grep 3002 2>/dev/null || echo "Port 3002 status unknown (need sudo)"
else
    netstat -tlnp | grep 3002 2>/dev/null || sudo netstat -tlnp | grep 3002 2>/dev/null || echo "Port 3002 status unknown (need sudo)"
fi

echo ""
echo "🧪 Testing Local Access:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" http://localhost:3002 || echo "Failed to connect"

echo ""
echo "🔥 Firewall Status:"
if command -v ufw &> /dev/null; then
    sudo ufw status | grep -E "3002|Status" || echo "UFW not configured or need sudo"
elif command -v firewall-cmd &> /dev/null; then
    sudo firewall-cmd --list-ports || echo "Firewalld not configured or need sudo"
else
    echo "No standard firewall detected"
fi

echo ""
echo "📋 Access URLs:"
echo "  Local: http://localhost:3002"
if command -v hostname &> /dev/null; then
    echo "  Hostname: http://$(hostname -f):3002 (if DNS configured)"
fi
if command -v ip &> /dev/null; then
    for ip in $(ip addr show | grep "inet " | grep -v "127.0.0.1" | awk '{print $2}' | cut -d'/' -f1); do
        echo "  IP: http://$ip:3002"
    done
fi

echo ""
echo "✅ Checklist:"
echo "  1. Did you run: ./rebuild.sh --prod --ip 0.0.0.0 --port 3002"
echo "  2. Is port 3002 open in your firewall?"
echo "  3. No VPN active that might block local network access?"
echo "  4. Using http:// not https:// in browser?"