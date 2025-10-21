#!/bin/bash
# =============================================================================
# Ventaura - View Service Logs
# =============================================================================
# This script displays logs from Docker containers
# Usage: 
#   ./docker-logs.sh           # All services
#   ./docker-logs.sh backend   # Backend only
#   ./docker-logs.sh ranking   # Ranking only
#   ./docker-logs.sh frontend  # Frontend only

set -e

SERVICE=${1:-""}

echo "=================================================="
echo "Ventaura Docker Logs"
echo "=================================================="
echo ""

if [ -z "$SERVICE" ]; then
    echo "Showing logs for ALL services (Ctrl+C to exit)..."
    echo ""
    docker-compose logs -f --tail=100
else
    echo "Showing logs for: $SERVICE (Ctrl+C to exit)..."
    echo ""
    docker-compose logs -f --tail=100 "$SERVICE"
fi

