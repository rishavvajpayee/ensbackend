# 🐳 Docker Deployment Guide

This guide will help you run the ENS Network Graph backend using Docker.

## 🎯 Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Docker Compose installed (usually comes with Docker Desktop)

## 🚀 Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up

# Or run in background
docker-compose up -d
```

### Option 2: Using the Start Script

```bash
# Make script executable (first time only)
chmod +x docker-start.sh

# Run the script
./docker-start.sh
```

## 📦 What's Included

The Docker setup includes:

1. **PostgreSQL Database** (port 5432)
   - Username: `ens_user`
   - Password: `ens_password`
   - Database: `ens_network`
   - Persistent volume for data storage

2. **FastAPI Backend** (port 8000)
   - Automatic database initialization
   - Test data seeding
   - Hot reload enabled for development

## 🔧 Configuration

### Environment Variables

The Docker setup uses these default values (defined in `docker-compose.yml`):

```yaml
DATABASE_URL: postgresql://ens_user:ens_password@postgres:5432/ens_network
SECRET_KEY: your-secret-key-change-in-production
ENVIRONMENT: development
```

To change them, edit `docker-compose.yml` or create a `.env` file.

### Ports

Default ports:
- **Backend**: `8000`
- **PostgreSQL**: `5432`

To change ports, modify `docker-compose.yml`:

```yaml
services:
  backend:
    ports:
      - "8001:8000"  # Host:Container
  postgres:
    ports:
      - "5433:5432"  # Host:Container
```

## 🛠️ Docker Commands

### Start Services

```bash
# Start and view logs
docker-compose up

# Start in background
docker-compose up -d

# Rebuild and start (after code changes)
docker-compose up --build
```

### Stop Services

```bash
# Stop services (keep data)
docker-compose down

# Stop and remove volumes (delete all data)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Access Containers

```bash
# Backend container shell
docker exec -it ens_backend sh

# PostgreSQL shell
docker exec -it ens_postgres psql -U ens_user -d ens_network

# Run SQL query
docker exec -it ens_postgres psql -U ens_user -d ens_network -c "SELECT * FROM friend_relationships;"
```

### Database Operations

```bash
# View tables
docker exec -it ens_postgres psql -U ens_user -d ens_network -c "\dt"

# View table structure
docker exec -it ens_postgres psql -U ens_user -d ens_network -c "\d friend_relationships"

# Backup database
docker exec ens_postgres pg_dump -U ens_user ens_network > backup.sql

# Restore database
cat backup.sql | docker exec -i ens_postgres psql -U ens_user -d ens_network
```

## 🔍 Monitoring

### Health Check

```bash
# Check if services are running
docker-compose ps

# Test API health
curl http://localhost:8000/health

# Or in browser
open http://localhost:8000/health
```

### API Documentation

Once running, access:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🐛 Troubleshooting

### Services Won't Start

```bash
# View detailed logs
docker-compose logs

# Check Docker status
docker ps -a

# Restart services
docker-compose restart
```

### Port Already in Use

If you see "port is already allocated":

1. Check what's using the port:
   ```bash
   lsof -i :8000  # Check port 8000
   lsof -i :5432  # Check port 5432
   ```

2. Stop the conflicting service or change ports in `docker-compose.yml`

### Database Connection Failed

```bash
# Check if PostgreSQL is ready
docker exec ens_postgres pg_isready

# View PostgreSQL logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Clear All Data and Restart

```bash
# Stop everything and remove volumes
docker-compose down -v

# Remove images (optional)
docker-compose down --rmi all

# Start fresh
docker-compose up --build
```

## 🔄 Development Workflow

### Making Code Changes

The backend code is mounted as a volume, so changes are reflected immediately:

1. Edit files in your IDE
2. FastAPI will auto-reload (watch the logs)
3. No need to restart containers

### Database Schema Changes

If you modify the database schema:

```bash
# Restart with fresh database
docker-compose down -v
docker-compose up
```

### Updating Dependencies

If you change `requirements.txt`:

```bash
# Rebuild the backend image
docker-compose up --build backend
```

## 📊 Resource Usage

Check resource usage:

```bash
# CPU and memory usage
docker stats

# Disk usage
docker system df
```

## 🧹 Cleanup

### Remove Stopped Containers

```bash
docker-compose down
```

### Remove All Data

```bash
# Remove volumes (database data)
docker-compose down -v
```

### Full Cleanup

```bash
# Remove everything (containers, volumes, networks)
docker-compose down -v --remove-orphans

# Remove unused Docker resources
docker system prune -a
```

## 🚀 Production Deployment

For production:

1. Change `SECRET_KEY` in `docker-compose.yml`
2. Use environment-specific `.env` file
3. Remove `--reload` flag from uvicorn command
4. Set up proper volume backups
5. Use Docker secrets for sensitive data
6. Configure proper logging
7. Set up monitoring and alerts

Example production changes in `docker-compose.yml`:

```yaml
backend:
  command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
  environment:
    ENVIRONMENT: production
  restart: always
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/)

---

**Need Help?** Check the main [README.md](README.md) for more information.

