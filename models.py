from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, UniqueConstraint, Index, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base


class Graph(Base):
    __tablename__ = "graphs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to friend_relationships
    relationships = relationship("FriendRelationship", back_populates="graph", cascade="all, delete-orphan")


class FriendRelationship(Base):
    __tablename__ = "friend_relationships"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ens_name_1 = Column(String(255), nullable=False, index=True)
    ens_name_2 = Column(String(255), nullable=False, index=True)
    graph_id = Column(Integer, ForeignKey('graphs.id', ondelete='CASCADE'), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationship to graph
    graph = relationship("Graph", back_populates="relationships")
    
    __table_args__ = (
        CheckConstraint('ens_name_1 != ens_name_2', name='no_self_relationship'),
        UniqueConstraint('ens_name_1', 'ens_name_2', 'graph_id', name='unique_relationship_per_graph'),
        Index('idx_ens_name_1', 'ens_name_1'),
        Index('idx_ens_name_2', 'ens_name_2'),
        Index('idx_graph_id', 'graph_id'),
    )

