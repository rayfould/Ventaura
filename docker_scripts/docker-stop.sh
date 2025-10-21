#!/bin/bash
# =============================================================================
# Ventaura - Stop All Services
# =============================================================================
# This script stops all running Docker containers for Ventaura
# Usage: ./docker-stop.sh

set -e

echo "=================================================="
echo "Stopping Ventaura Docker Services"
echo "=================================================="

docker-compose down

echo ""
echo "All services stopped successfully!"
echo ""

