from pydantic import BaseModel, field_validator
from datetime import datetime
from typing import Optional

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
    
    class Config:
        from_attributes = True

class RelationshipDelete(BaseModel):
    ens_name_1: str
    ens_name_2: str

class HealthResponse(BaseModel):
    status: str
    database: str
    timestamp: datetime

