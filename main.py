from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
from typing import List

from database import engine, get_db, Base
from models import FriendRelationship, Graph
from schemas import (
    RelationshipCreate,
    RelationshipResponse,
    RelationshipDelete,
    HealthResponse,
    GraphCreate,
    GraphResponse,
    GraphWithRelationships
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ENS Network Graph API",
    description="API for managing friend relationships between ENS names",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def normalize_relationship(name1: str, name2: str) -> tuple:
    """Return names in alphabetical order to ensure consistency"""
    return tuple(sorted([name1, name2]))


@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify backend availability"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        database_status = "connected"
    except Exception:
        database_status = "disconnected"
    
    return {
        "status": "healthy",
        "database": database_status,
        "timestamp": datetime.utcnow()
    }


# =============================================================================
# GRAPH MANAGEMENT ENDPOINTS
# =============================================================================

@app.get("/api/graphs", response_model=List[GraphResponse])
async def get_all_graphs(db: Session = Depends(get_db)):
    """Retrieve all graphs with their relationship counts"""
    try:
        graphs = db.query(Graph).order_by(Graph.created_at.desc()).all()
        
        # Add relationship count to each graph
        result = []
        for graph in graphs:
            graph_dict = {
                "id": graph.id,
                "name": graph.name,
                "description": graph.description,
                "created_at": graph.created_at,
                "updated_at": graph.updated_at,
                "relationship_count": len(graph.relationships)
            }
            result.append(graph_dict)
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve graphs: {str(e)}"
        )


@app.get("/api/graphs/{graph_id}", response_model=GraphWithRelationships)
async def get_graph(graph_id: int, db: Session = Depends(get_db)):
    """Get a specific graph with all its relationships"""
    graph = db.query(Graph).filter(Graph.id == graph_id).first()
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph with id {graph_id} not found"
        )
    
    return graph


@app.post("/api/graphs", response_model=GraphResponse, status_code=status.HTTP_201_CREATED)
async def create_graph(graph: GraphCreate, db: Session = Depends(get_db)):
    """Create a new graph"""
    
    # Check if a graph with this name already exists
    existing_graph = db.query(Graph).filter(Graph.name == graph.name).first()
    
    if existing_graph:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Graph with name '{graph.name}' already exists"
        )
    
    # Create new graph
    new_graph = Graph(
        name=graph.name,
        description=graph.description
    )
    
    try:
        db.add(new_graph)
        db.commit()
        db.refresh(new_graph)
        
        return {
            "id": new_graph.id,
            "name": new_graph.name,
            "description": new_graph.description,
            "created_at": new_graph.created_at,
            "updated_at": new_graph.updated_at,
            "relationship_count": 0
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create graph: {str(e)}"
        )


@app.delete("/api/graphs/{graph_id}")
async def delete_graph(graph_id: int, db: Session = Depends(get_db)):
    """Delete a graph and all its associated relationships"""
    graph = db.query(Graph).filter(Graph.id == graph_id).first()
    
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph with id {graph_id} not found"
        )
    
    try:
        db.delete(graph)
        db.commit()
        
        return {
            "message": "Graph deleted successfully",
            "deleted_id": graph_id
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete graph: {str(e)}"
        )


@app.post("/api/graphs/{graph_id}/relationships", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED)
async def add_relationship_to_graph(
    graph_id: int,
    relationship: RelationshipCreate,
    db: Session = Depends(get_db)
):
    """Add a new relationship to a specific graph"""
    
    # Check if graph exists
    graph = db.query(Graph).filter(Graph.id == graph_id).first()
    if not graph:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Graph with id {graph_id} not found"
        )
    
    # Normalize the names to prevent duplicates
    name1, name2 = normalize_relationship(
        relationship.ens_name_1,
        relationship.ens_name_2
    )
    
    # Check if relationship already exists in this graph
    existing = db.query(FriendRelationship).filter(
        FriendRelationship.ens_name_1 == name1,
        FriendRelationship.ens_name_2 == name2,
        FriendRelationship.graph_id == graph_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Relationship between {name1} and {name2} already exists in this graph"
        )
    
    # Create new relationship
    new_relationship = FriendRelationship(
        ens_name_1=name1,
        ens_name_2=name2,
        graph_id=graph_id
    )
    
    try:
        db.add(new_relationship)
        db.commit()
        db.refresh(new_relationship)
        
        return new_relationship
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create relationship: {str(e)}"
        )


# =============================================================================
# RELATIONSHIP ENDPOINTS (Legacy - for backward compatibility)
# =============================================================================

@app.get("/api/relationships", response_model=List[RelationshipResponse])
async def get_all_relationships(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Retrieve all friend relationships from the database"""
    try:
        relationships = db.query(FriendRelationship)\
            .offset(offset)\
            .limit(limit)\
            .all()
        return relationships
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection error"
        )


@app.get("/api/relationships/{ens_name}", response_model=List[RelationshipResponse])
async def get_relationships_by_ens_name(
    ens_name: str,
    db: Session = Depends(get_db)
):
    """Get all relationships for a specific ENS name"""
    relationships = db.query(FriendRelationship).filter(
        or_(
            FriendRelationship.ens_name_1 == ens_name,
            FriendRelationship.ens_name_2 == ens_name
        )
    ).all()
    
    if not relationships:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No relationships found for {ens_name}"
        )
    
    return relationships


@app.post("/api/relationships", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    relationship: RelationshipCreate,
    db: Session = Depends(get_db)
):
    """Create a new friend relationship between two ENS names"""
    
    # Normalize the names to prevent duplicates
    name1, name2 = normalize_relationship(
        relationship.ens_name_1,
        relationship.ens_name_2
    )
    
    # Check if relationship already exists
    existing = db.query(FriendRelationship).filter(
        FriendRelationship.ens_name_1 == name1,
        FriendRelationship.ens_name_2 == name2
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Relationship between {name1} and {name2} already exists"
        )
    
    # Create new relationship
    new_relationship = FriendRelationship(
        ens_name_1=name1,
        ens_name_2=name2
    )
    
    try:
        db.add(new_relationship)
        db.commit()
        db.refresh(new_relationship)
        
        return {
            "id": new_relationship.id,
            "ens_name_1": new_relationship.ens_name_1,
            "ens_name_2": new_relationship.ens_name_2,
            "created_at": new_relationship.created_at,
            "message": "Relationship created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ENS names provided"
        )


@app.delete("/api/relationships/delete-by-names")
async def delete_relationship_by_names_query(
    ens_name_1: str = Query(..., description="First ENS name"),
    ens_name_2: str = Query(..., description="Second ENS name"),
    db: Session = Depends(get_db)
):
    """Delete a relationship by ENS names using query parameters"""
    
    if not ens_name_1 or not ens_name_2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both ens_name_1 and ens_name_2 are required"
        )
    
    # Normalize the names to match how they're stored
    name1, name2 = normalize_relationship(ens_name_1, ens_name_2)
    
    # Find and delete the relationship
    relationship = db.query(FriendRelationship).filter(
        FriendRelationship.ens_name_1 == name1,
        FriendRelationship.ens_name_2 == name2
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship between {ens_name_1} and {ens_name_2} not found"
        )
    
    try:
        db.delete(relationship)
        db.commit()
        
        return {
            "message": "Relationship deleted successfully",
            "ens_name_1": ens_name_1,
            "ens_name_2": ens_name_2
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@app.delete("/api/relationships/{relationship_id}")
async def delete_relationship_by_id(
    relationship_id: int,
    db: Session = Depends(get_db)
):
    """Delete a specific relationship by its ID"""
    relationship = db.query(FriendRelationship).filter(
        FriendRelationship.id == relationship_id
    ).first()
    
    if not relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship with id {relationship_id} not found"
        )
    
    db.delete(relationship)
    db.commit()
    
    return {
        "message": "Relationship deleted successfully",
        "deleted_id": relationship_id
    }


@app.delete("/api/relationships/by-names")
async def delete_relationship_by_names(
    relationship: RelationshipDelete,
    db: Session = Depends(get_db)
):
    """Delete a relationship by specifying both ENS names"""
    
    if not relationship.ens_name_1 or not relationship.ens_name_2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Both ens_name_1 and ens_name_2 are required"
        )
    
    # Normalize the names
    name1, name2 = normalize_relationship(
        relationship.ens_name_1,
        relationship.ens_name_2
    )
    
    # Find and delete the relationship
    db_relationship = db.query(FriendRelationship).filter(
        FriendRelationship.ens_name_1 == name1,
        FriendRelationship.ens_name_2 == name2
    ).first()
    
    if not db_relationship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Relationship between {relationship.ens_name_1} and {relationship.ens_name_2} not found"
        )
    
    db.delete(db_relationship)
    db.commit()
    
    return {
        "message": "Relationship deleted successfully",
        "ens_name_1": relationship.ens_name_1,
        "ens_name_2": relationship.ens_name_2
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

