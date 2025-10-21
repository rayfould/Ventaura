#!/bin/bash
# =============================================================================
# Ventaura - Check Service Status
# =============================================================================
# This script shows the status of all Docker containers
# Usage: ./docker-status.sh

set -e

echo "=================================================="
echo "Ventaura Docker Status"
echo "=================================================="
echo ""

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "No services are currently running."
    echo ""
    echo "To start services, run: ./docker-start.sh"
    echo ""
else
    echo "Running Services:"
    echo ""
    docker-compose ps
    echo ""
    echo "=================================================="
    echo ""
    echo "Quick Actions:"
    echo "  View logs:     ./docker-logs.sh"
    echo "  Stop services: ./docker-stop.sh"
    echo "  Restart:       ./docker-rebuild.sh"
    echo ""
fi

