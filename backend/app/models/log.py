from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Log(Base):
    """Audit log model"""
    __tablename__ = "logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User (nullable for system actions)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Action details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50), nullable=True)  # vm, user, server, template
    resource_id = Column(Integer, nullable=True)
    
    # Request details
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Details & result
    details = Column(JSON, nullable=True)
    status = Column(String(20), nullable=True)  # success, error, warning
    error_message = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="logs")
    
    def __repr__(self):
        return f"<Log(id={self.id}, action={self.action}, user_id={self.user_id})>"
