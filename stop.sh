#!/bin/bash

# Stop the Security Analyst Platform

echo "🛑 Stopping Security Analyst Platform..."

if [ -f docker-compose.override.yml ]; then
    docker compose -f docker-compose.test.yml -f docker-compose.override.yml down
else
    docker compose -f docker-compose.test.yml down
fi

echo "✅ Services stopped"