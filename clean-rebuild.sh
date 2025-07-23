#!/bin/bash

echo "🧹 Clean rebuild of Security Platform"
echo "===================================="
echo ""

# Stop all services
echo "🛑 Stopping all services..."
./stop.sh

# Remove all containers and images
echo "🗑️  Removing old containers and images..."
docker compose -f docker-compose.prod.yml down --rmi all --volumes 2>/dev/null || true
docker compose down --rmi all --volumes 2>/dev/null || true

# Remove any dangling images
docker image prune -f

echo ""
echo "🔨 Starting fresh build..."
echo ""

# Run the rebuild with production flag
./rebuild.sh --prod "$@"