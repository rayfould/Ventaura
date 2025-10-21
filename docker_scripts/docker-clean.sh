#!/bin/bash
# =============================================================================
# Ventaura - Clean Docker Environment
# =============================================================================
# This script removes all containers, networks, and optionally images
# WARNING: This will delete all data in containers!
# Usage: 
#   ./docker-clean.sh        # Remove containers and networks
#   ./docker-clean.sh --all  # Also remove images and volumes

set -e

echo "=================================================="
echo "Ventaura Docker Cleanup"
echo "=================================================="
echo ""
echo "WARNING: This will stop and remove all Ventaura containers!"
echo ""
read -p "Are you sure? (yes/no): " -r
echo ""

if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo "Stopping and removing containers..."
docker-compose down

if [ "$1" == "--all" ]; then
    echo ""
    echo "Removing images..."
    docker-compose down --rmi all
    
    echo ""
    echo "Removing volumes..."
    docker-compose down --volumes
    
    echo ""
    echo "Full cleanup complete!"
    echo "Next start will rebuild everything from scratch."
else
    echo ""
    echo "Containers and networks removed."
    echo "Images and volumes preserved."
    echo ""
    echo "To remove everything, run: ./docker-clean.sh --all"
fi

echo ""
echo "=================================================="

