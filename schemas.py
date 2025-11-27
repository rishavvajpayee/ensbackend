from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional, List

class RelationshipCreate(BaseModel):
    ens_name_1: str
    ens_name_2: str
    
    @field_validator('ens_name_1', 'ens_name_2')
    @classmethod
    def validate_ens_name(cls, v):
        if not v or not v.strip():
            raise ValueError('ENS name cannot be empty')
        return v.strip()
    
    @field_validator('ens_name_2')
    @classmethod
    def validate_not_self(cls, v, info):
        if 'ens_name_1' in info.data and v == info.data['ens_name_1']:
            raise ValueError('Self-relationships are not allowed')
        return v

class RelationshipResponse(BaseModel):
    id: int
    ens_name_1: str
    ens_name_2: str
    created_at: datetime
    graph_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class RelationshipDelete(BaseModel):
    ens_name_1: str
    ens_name_2: str

class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime


# Graph-related schemas
class GraphCreate(BaseModel):
    name: str
    description: Optional[str] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Graph name cannot be empty')
        return v.strip()

class GraphResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    relationship_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class GraphWithRelationships(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    relationships: List[RelationshipResponse] = []
    
    class Config:
        from_attributes = True

