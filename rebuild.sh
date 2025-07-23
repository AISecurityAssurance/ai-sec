#!/bin/bash

# Stop and remove existing containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true
docker compose -f docker-compose.prod.yml down 2>/dev/null || true

# Clear docker build cache for frontend (to ensure CSS changes are picked up)
echo "Clearing frontend build cache..."
docker rmi prototype1-frontend 2>/dev/null || true

# Check if production flag is set
if [[ "$1" == "--prod" ]] || [[ "$2" == "--prod" ]] || [[ "$3" == "--prod" ]] || [[ "$4" == "--prod" ]]; then
    echo "Using production setup with nginx (recommended for remote access)..."
    # Remove --prod from arguments before passing to setup-prod.sh
    ARGS=()
    for arg in "$@"; do
        if [[ "$arg" != "--prod" ]]; then
            ARGS+=("$arg")
        fi
    done
    ./setup-prod.sh "${ARGS[@]}"
else
    echo "Using development setup with Vite..."
    echo "Note: For remote access, use --prod flag (e.g., ./rebuild.sh --prod --ip 0.0.0.0 --port 3002)"
    ./setup.sh "$@"
fi

echo ""
echo "Build complete! The application should now be running."
echo "If demo mode is still enabled, try clearing your browser's localStorage for this site."