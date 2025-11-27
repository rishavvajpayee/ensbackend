from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, UniqueConstraint, Index
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
        Index('idx_ens_name_1', 'ens_name_1'),
        Index('idx_ens_name_2', 'ens_name_2'),
    )

