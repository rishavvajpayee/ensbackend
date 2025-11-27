#!/bin/bash

echo "🧹 Cleaning up Docker containers and volumes..."

# Stop all containers
docker-compose down 2>/dev/null || true

# Stop and remove any lingering postgres containers
docker stop ens_postgres ens_backend 2>/dev/null || true
docker rm ens_postgres ens_backend 2>/dev/null || true

# Remove the problematic volume
docker volume rm backend_postgres_data 2>/dev/null || true

# Prune any dangling volumes
docker volume prune -f

echo "✅ Cleanup complete!"
echo ""
echo "🚀 Starting fresh containers..."

# Start services
docker-compose up -d --build

echo ""
echo "⏳ Waiting for services to start..."
sleep 15

# Check status
docker-compose ps

echo ""
echo "📋 Backend logs:"
docker logs ens_backend --tail 20

echo ""
echo "🎉 Done! Check http://localhost:8000/docs"

