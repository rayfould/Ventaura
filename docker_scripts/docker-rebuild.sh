#!/bin/bash
# =============================================================================
# Ventaura - Rebuild and Restart All Services
# =============================================================================
# This script rebuilds Docker images and restarts all containers
# Useful after code changes
# Usage: ./docker-rebuild.sh

set -e

echo "=================================================="
echo "Rebuilding Ventaura Docker Services"
echo "=================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please rename env.txt to .env and populate it with your values."
    exit 1
fi

echo ""
echo "Stopping existing containers..."
docker-compose down

echo ""
echo "Rebuilding images (no cache)..."
docker-compose build --no-cache

echo ""
echo "Starting services..."
docker-compose up -d

echo ""
echo "=================================================="
echo "Rebuild Complete!"
echo "=================================================="
echo ""
echo "Services are now running with fresh builds."
echo ""
echo "View logs:"
echo "  docker-compose logs -f"
echo ""

