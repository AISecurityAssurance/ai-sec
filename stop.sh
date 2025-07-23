#\!/bin/bash

echo "🛑 Stopping all Security Platform services..."

# Stop development services
docker-compose down 2>/dev/null || true

# Stop production services
docker compose -f docker-compose.prod.yml down 2>/dev/null || true

# Stop test services
docker compose -f docker-compose.test.yml down 2>/dev/null || true

echo "✅ All services stopped."
EOF < /dev/null
