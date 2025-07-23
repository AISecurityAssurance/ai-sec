#!/bin/bash

# Stop and remove existing containers
echo "Stopping existing containers..."
docker-compose down

# Clear docker build cache for frontend (to ensure CSS changes are picked up)
echo "Clearing frontend build cache..."
docker rmi prototype1-frontend 2>/dev/null || true

# Rebuild and start
echo "Rebuilding and starting services..."
./setup.sh "$@"

echo "Build complete! The application should now be running."
echo "If demo mode is still enabled, try clearing your browser's localStorage for this site."