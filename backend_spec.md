# Backend API Specification for ENS Network Graph

## Overview
This document provides comprehensive specifications for the FastAPI backend that will power the ENS Network Graph application. The backend is responsible for managing friend relationships between ENS names, stored in a PostgreSQL database.

## Technology Stack
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy (recommended) or any Python ORM
- **CORS**: Enable CORS for frontend communication

## Base URL
```
http://localhost:8000
```

---

## Database Schema

### Table: `friend_relationships`

| Column       | Type         | Constraints                    | Description                           |
|--------------|--------------|--------------------------------|---------------------------------------|
| id           | INTEGER      | PRIMARY KEY, AUTO_INCREMENT    | Unique identifier for the relationship|
| ens_name_1   | VARCHAR(255) | NOT NULL, INDEX                | First ENS name in the relationship    |
| ens_name_2   | VARCHAR(255) | NOT NULL, INDEX                | Second ENS name in the relationship   |
| created_at   | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP      | When the relationship was created     |
| updated_at   | TIMESTAMP    | DEFAULT CURRENT_TIMESTAMP, ON UPDATE | Last update timestamp         |

#### Additional Constraints:
- Create a **UNIQUE constraint** on `(ens_name_1, ens_name_2)` to prevent duplicate relationships
- Consider: Normalize the order (e.g., alphabetically sort names) so (A, B) and (B, A) are treated as the same relationship
- Add **CHECK constraint**: `ens_name_1 != ens_name_2` (prevent self-relationships)

#### Indexes:
```sql
CREATE INDEX idx_ens_name_1 ON friend_relationships(ens_name_1);
CREATE INDEX idx_ens_name_2 ON friend_relationships(ens_name_2);
CREATE UNIQUE INDEX idx_unique_relationship ON friend_relationships(ens_name_1, ens_name_2);
```

---

## API Endpoints

### 1. Health Check
**Purpose**: Verify backend availability

**Endpoint**: `GET /health`

**Response**: `200 OK`
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-27T10:00:00Z"
}
```

---

### 2. Get All Relationships
**Purpose**: Retrieve all friend relationships from the database

**Endpoint**: `GET /api/relationships`

**Query Parameters**:
- `limit` (optional): Number of results to return (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "ens_name_1": "vitalik.eth",
    "ens_name_2": "nick.eth",
    "created_at": "2025-11-27T10:00:00Z"
  },
  {
    "id": 2,
    "ens_name_1": "vitalik.eth",
    "ens_name_2": "brantly.eth",
    "created_at": "2025-11-27T10:05:00Z"
  }
]
```

**Error Responses**:
- `500 Internal Server Error`: Database connection failed
```json
{
  "detail": "Database connection error"
}
```

---

### 3. Get Relationships by ENS Name
**Purpose**: Get all relationships for a specific ENS name

**Endpoint**: `GET /api/relationships/{ens_name}`

**Path Parameters**:
- `ens_name`: The ENS name to query (e.g., "vitalik.eth")

**Response**: `200 OK`
```json
[
  {
    "id": 1,
    "ens_name_1": "vitalik.eth",
    "ens_name_2": "nick.eth",
    "created_at": "2025-11-27T10:00:00Z"
  },
  {
    "id": 2,
    "ens_name_1": "vitalik.eth",
    "ens_name_2": "brantly.eth",
    "created_at": "2025-11-27T10:05:00Z"
  }
]
```

**Error Responses**:
- `404 Not Found`: No relationships found for this ENS name
```json
{
  "detail": "No relationships found for vitalik.eth"
}
```

---

### 4. Add New Relationship
**Purpose**: Create a new friend relationship between two ENS names

**Endpoint**: `POST /api/relationships`

**Request Body**:
```json
{
  "ens_name_1": "vitalik.eth",
  "ens_name_2": "nick.eth"
}
```

**Validation Rules**:
1. Both `ens_name_1` and `ens_name_2` are required
2. Names must not be empty or just whitespace
3. Names should be valid ENS format (optional: validate with regex `^[a-zA-Z0-9\-\.]+$`)
4. `ens_name_1` must not equal `ens_name_2` (no self-relationships)
5. Normalize the order before insertion to prevent duplicates

**Response**: `201 Created`
```json
{
  "id": 3,
  "ens_name_1": "vitalik.eth",
  "ens_name_2": "nick.eth",
  "created_at": "2025-11-27T10:10:00Z",
  "message": "Relationship created successfully"
}
```

**Error Responses**:
- `400 Bad Request`: Invalid input
```json
{
  "detail": "Invalid ENS names provided"
}
```

- `409 Conflict`: Relationship already exists
```json
{
  "detail": "Relationship between vitalik.eth and nick.eth already exists"
}
```

- `422 Unprocessable Entity`: Validation error
```json
{
  "detail": "Self-relationships are not allowed"
}
```

---

### 5. Delete Relationship by ID
**Purpose**: Delete a specific relationship by its ID

**Endpoint**: `DELETE /api/relationships/{relationship_id}`

**Path Parameters**:
- `relationship_id`: The ID of the relationship to delete

**Response**: `200 OK`
```json
{
  "message": "Relationship deleted successfully",
  "deleted_id": 3
}
```

**Error Responses**:
- `404 Not Found`: Relationship doesn't exist
```json
{
  "detail": "Relationship with id 3 not found"
}
```

---

### 6. Delete Relationship by ENS Names
**Purpose**: Delete a relationship by specifying both ENS names

**Endpoint**: `DELETE /api/relationships/by-names`

**Request Body**:
```json
{
  "ens_name_1": "vitalik.eth",
  "ens_name_2": "nick.eth"
}
```

**Note**: The order shouldn't matter - normalize before querying

**Response**: `200 OK`
```json
{
  "message": "Relationship deleted successfully",
  "ens_name_1": "vitalik.eth",
  "ens_name_2": "nick.eth"
}
```

**Error Responses**:
- `404 Not Found`: Relationship doesn't exist
```json
{
  "detail": "Relationship between vitalik.eth and nick.eth not found"
}
```

- `400 Bad Request`: Invalid input
```json
{
  "detail": "Both ens_name_1 and ens_name_2 are required"
}
```

---

## Implementation Details

### CORS Configuration
Enable CORS to allow frontend requests from `http://localhost:3000`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Example SQLAlchemy Model

```python
from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, UniqueConstraint
from sqlalchemy.sql import func
from database import Base

class FriendRelationship(Base):
    __tablename__ = "friend_relationships"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ens_name_1 = Column(String(255), nullable=False, index=True)
    ens_name_2 = Column(String(255), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint('ens_name_1 != ens_name_2', name='no_self_relationship'),
        UniqueConstraint('ens_name_1', 'ens_name_2', name='unique_relationship'),
    )
```

### Example Pydantic Models

```python
from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional

class RelationshipCreate(BaseModel):
    ens_name_1: str
    ens_name_2: str
    
    @validator('ens_name_1', 'ens_name_2')
    def validate_ens_name(cls, v):
        if not v or not v.strip():
            raise ValueError('ENS name cannot be empty')
        return v.strip()
    
    @validator('ens_name_2')
    def validate_not_self(cls, v, values):
        if 'ens_name_1' in values and v == values['ens_name_1']:
            raise ValueError('Self-relationships are not allowed')
        return v

class RelationshipResponse(BaseModel):
    id: int
    ens_name_1: str
    ens_name_2: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class RelationshipDelete(BaseModel):
    ens_name_1: str
    ens_name_2: str
```

### Normalization Function

To prevent duplicate relationships like (A, B) and (B, A):

```python
def normalize_relationship(name1: str, name2: str) -> tuple:
    """Return names in alphabetical order to ensure consistency"""
    return tuple(sorted([name1, name2]))

# Usage in endpoint:
@app.post("/api/relationships")
def create_relationship(relationship: RelationshipCreate):
    name1, name2 = normalize_relationship(
        relationship.ens_name_1, 
        relationship.ens_name_2
    )
    # Create relationship with normalized names
    # ...
```

---

## Database Setup

### PostgreSQL Connection String
```
postgresql://username:password@localhost:5432/ens_network
```

### Environment Variables
Create a `.env` file:
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/ens_network
SECRET_KEY=your-secret-key-here
ENVIRONMENT=development
```

### Initial Migration Script
```sql
CREATE TABLE IF NOT EXISTS friend_relationships (
    id SERIAL PRIMARY KEY,
    ens_name_1 VARCHAR(255) NOT NULL,
    ens_name_2 VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT no_self_relationship CHECK (ens_name_1 != ens_name_2),
    CONSTRAINT unique_relationship UNIQUE (ens_name_1, ens_name_2)
);

CREATE INDEX idx_ens_name_1 ON friend_relationships(ens_name_1);
CREATE INDEX idx_ens_name_2 ON friend_relationships(ens_name_2);
```

---

## Testing Requirements

### Test Data
Provide seed data for testing:
```sql
INSERT INTO friend_relationships (ens_name_1, ens_name_2) VALUES
    ('vitalik.eth', 'nick.eth'),
    ('vitalik.eth', 'brantly.eth'),
    ('nick.eth', 'brantly.eth');
```

### Test Cases to Implement
1. ✅ Create a new relationship
2. ✅ Prevent duplicate relationships
3. ✅ Prevent self-relationships
4. ✅ Retrieve all relationships
5. ✅ Retrieve relationships by ENS name
6. ✅ Delete relationship by ID
7. ✅ Delete relationship by names
8. ✅ Handle invalid ENS names
9. ✅ Handle database connection errors
10. ✅ Test CORS headers

---

## Security Considerations

1. **Input Validation**: Sanitize all ENS name inputs to prevent SQL injection
2. **Rate Limiting**: Implement rate limiting on POST/DELETE endpoints
3. **Authentication** (Future): Consider adding API key authentication
4. **SQL Injection Prevention**: Use parameterized queries (handled by ORM)
5. **Error Messages**: Don't expose internal server details in error messages

---

## Performance Recommendations

1. **Indexing**: Ensure indexes are created on `ens_name_1` and `ens_name_2`
2. **Pagination**: Implement pagination for large datasets
3. **Connection Pooling**: Use database connection pooling
4. **Caching**: Consider Redis for frequently accessed relationships
5. **Query Optimization**: Use `EXPLAIN ANALYZE` to optimize slow queries

---

## Development Workflow

### 1. Setup Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv pydantic
```

### 3. Run Development Server
```bash
uvicorn main:app --reload --port 8000
```

### 4. API Documentation
FastAPI provides automatic documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Deployment Checklist

- [ ] Set up PostgreSQL database
- [ ] Configure environment variables
- [ ] Run database migrations
- [ ] Test all API endpoints
- [ ] Enable CORS for production frontend URL
- [ ] Set up error logging (e.g., Sentry)
- [ ] Configure rate limiting
- [ ] Set up database backups
- [ ] Add health check monitoring
- [ ] Document deployment process

---

## Support & Contact

**Frontend Repository**: Link to your frontend repo  
**Expected Response Time**: Coordinate with frontend team  
**API Version**: 1.0.0

---

## Example `requirements.txt`

```txt
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0
```

---

## Quick Start Command

```bash
# Clone and setup
git clone <backend-repo>
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup database
createdb ens_network
python init_db.py

# Run server
uvicorn main:app --reload --port 8000
```

---

**Last Updated**: 2025-11-27  
**API Version**: 1.0.0  
**Status**: Ready for Implementation

