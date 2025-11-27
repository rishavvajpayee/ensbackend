# ENS Network Graph - Backend API

A FastAPI backend for managing friend relationships between ENS names with PostgreSQL database.

## 🐳 Docker Quick Start (Recommended)

The easiest way to run the application is using Docker Compose:

### Prerequisites
- Docker
- Docker Compose

### Run with Docker

```bash
# Start the application (backend + PostgreSQL)
docker-compose up

# Or run in detached mode
docker-compose up -d
```

That's it! The application will:
- ✅ Start PostgreSQL database
- ✅ Create database tables
- ✅ Seed test data
- ✅ Start FastAPI server

**Access the API:**
- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Management

```bash
# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (delete all data)
docker-compose down -v

# Rebuild after code changes
docker-compose up --build

# Access backend container shell
docker exec -it ens_backend sh

# Access PostgreSQL
docker exec -it ens_postgres psql -U ens_user -d ens_network
```

---

## 🚀 Manual Setup (Without Docker)

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

### 1. Setup Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```
DATABASE_URL=postgresql://username:password@localhost:5432/ens_network
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
```

### 4. Setup Database

Create the database:

```bash
createdb ens_network
```

Initialize tables and seed test data:

```bash
python init_db.py
```

### 5. Run Development Server

```bash
uvicorn main:app --reload --port 8000
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once the server is running, access interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Health Check
- `GET /health` - Check API and database status

### Relationships
- `GET /api/relationships` - Get all relationships (with pagination)
- `GET /api/relationships/{ens_name}` - Get relationships for specific ENS name
- `POST /api/relationships` - Create new relationship
- `DELETE /api/relationships/{relationship_id}` - Delete relationship by ID
- `DELETE /api/relationships/by-names` - Delete relationship by ENS names

## 📝 Example Usage

### Create a Relationship

```bash
curl -X POST "http://localhost:8000/api/relationships" \
  -H "Content-Type: application/json" \
  -d '{"ens_name_1": "vitalik.eth", "ens_name_2": "nick.eth"}'
```

### Get All Relationships

```bash
curl "http://localhost:8000/api/relationships"
```

### Get Relationships for Specific ENS Name

```bash
curl "http://localhost:8000/api/relationships/vitalik.eth"
```

### Delete Relationship by ID

```bash
curl -X DELETE "http://localhost:8000/api/relationships/1"
```

### Delete Relationship by Names

```bash
curl -X DELETE "http://localhost:8000/api/relationships/by-names" \
  -H "Content-Type: application/json" \
  -d '{"ens_name_1": "vitalik.eth", "ens_name_2": "nick.eth"}'
```

## 🏗️ Project Structure

```
backend/
├── main.py              # FastAPI application and endpoints
├── database.py          # Database connection and session
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── init_db.py           # Database initialization script
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── .dockerignore        # Docker ignore file
├── .env.example         # Environment variables template
├── .env.docker          # Docker environment template
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## 🔒 Security Features

- Input validation for all ENS names
- Prevention of duplicate relationships
- Prevention of self-relationships
- SQL injection protection via ORM
- CORS configuration for frontend

## 🧪 Testing

The database initialization script includes test data:
- vitalik.eth ↔ nick.eth
- vitalik.eth ↔ brantly.eth
- nick.eth ↔ brantly.eth

## 🛠️ Development

### Database Migrations

To reset the database:

```bash
dropdb ens_network
createdb ens_network
python init_db.py
```

### Running in Production

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📦 Dependencies

- **FastAPI**: Modern web framework
- **Uvicorn**: ASGI server
- **SQLAlchemy**: ORM for database operations
- **Psycopg2**: PostgreSQL adapter
- **Pydantic**: Data validation
- **Python-dotenv**: Environment variable management

## 🐛 Troubleshooting

### Docker Issues

**Containers not starting:**
```bash
# Check container logs
docker-compose logs

# Restart services
docker-compose restart
```

**Port conflicts:**
```bash
# If ports 8000 or 5432 are in use, modify docker-compose.yml:
ports:
  - "8001:8000"  # Change host port
```

**Database connection issues:**
```bash
# Check if PostgreSQL is ready
docker-compose exec postgres pg_isready

# View database
docker-compose exec postgres psql -U ens_user -d ens_network -c "\dt"
```

### Database Connection Issues (Manual Setup)

If you see "Database connection error":
1. Check if PostgreSQL is running: `pg_isready`
2. Verify database exists: `psql -l | grep ens_network`
3. Check credentials in `.env` file

### Port Already in Use

If port 8000 is busy, use a different port:

```bash
uvicorn main:app --reload --port 8001
```

## 📄 License

MIT

## 👥 Support

For issues or questions, please refer to the project documentation.

---

**API Version**: 1.0.0  
**Last Updated**: 2025-11-27

