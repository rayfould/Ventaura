#!/bin/bash
# =============================================================================
# Ventaura - Start All Services
# =============================================================================
# This script starts all Docker containers for the Ventaura application
# Usage: ./docker-start.sh

set -e

echo "=================================================="
echo "Starting Ventaura Docker Services"
echo "=================================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please rename env.txt to .env and populate it with your values."
    echo ""
    echo "Steps:"
    echo "  1. cp env.txt .env"
    echo "  2. Edit .env and fill in all FILL_ME_IN values"
    echo "  3. Run this script again"
    exit 1
fi

echo ""
echo "Building and starting services..."
echo "This may take a few minutes on first run..."
echo ""

# Start services with docker-compose
docker-compose up -d --build

echo ""
echo "=================================================="
echo "Services Started Successfully!"
echo "=================================================="
echo ""
echo "Access URLs:"
echo "  Frontend:  http://localhost:3000"
echo "  Backend:   http://localhost:5152"
echo "  Ranking:   http://localhost:8000"
echo ""
echo "View logs:"
echo "  All services:     docker-compose logs -f"
echo "  Backend only:     docker-compose logs -f backend"
echo "  Ranking only:     docker-compose logs -f ranking"
echo "  Frontend only:    docker-compose logs -f frontend"
echo ""
echo "Check status:"
echo "  docker-compose ps"
echo ""
echo "=================================================="

