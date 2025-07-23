#!/bin/bash

echo "🧹 Cleaning Docker cache and containers"
echo "======================================"

# Stop all containers
echo "Stopping all containers..."
docker stop $(docker ps -aq) 2>/dev/null || true

# Remove all containers
echo "Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null || true

# Remove all images related to the project
echo "Removing project images..."
docker rmi $(docker images -q prototype1*) 2>/dev/null || true

# Clean build cache
echo "Cleaning build cache..."
docker builder prune -f

# Clean system
echo "Cleaning Docker system..."
docker system prune -f

# Clean volumes (be careful with this)
echo "Cleaning unused volumes..."
docker volume prune -f

echo ""
echo "✅ Docker cleanup complete!"
echo ""
echo "You can now run the integration tests again:"
echo "./integration-tests/run-integration-tests.sh"