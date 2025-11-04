from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, JSON, Text
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base


class TaskStatus(str, enum.Enum):
    """Background task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Task(Base):
    """Background task model"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Task details
    type = Column(String(100), nullable=False, index=True)  # vm_create, billing_cycle, etc.
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    
    # Payload & result
    payload = Column(JSON, nullable=True)  # Input parameters
    result = Column(JSON, nullable=True)  # Output data
    error_message = Column(Text, nullable=True)
    
    # Celery task ID
    celery_task_id = Column(String(255), nullable=True, index=True)
    
    # Progress tracking
    progress_percent = Column(Integer, default=0)
    progress_message = Column(String(500), nullable=True)
    
    # Execution times
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Task(id={self.id}, type={self.type}, status={self.status})>"
    
    @property
    def duration_seconds(self) -> float:
        """Calculate task duration in seconds"""
        if not self.started_at:
            return 0.0
        
        end_time = self.completed_at or datetime.utcnow()
        delta = end_time - self.started_at.replace(tzinfo=None)
        return delta.total_seconds()
