from sqlalchemy import Column, Integer, String, DateTime, Numeric, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles"""
    USER = "user"
    OPERATOR = "operator"
    ADMIN = "admin"


class UserStatus(str, enum.Enum):
    """User account status"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"


class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    balance = Column(Numeric(10, 2), default=0.00, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    
    # Ban information
    ban_reason = Column(String(500), nullable=True)
    ban_until = Column(DateTime(timezone=True), nullable=True)  # None = permanent ban
    
    # Profile
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    company = Column(String(200), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    vms = relationship("VM", back_populates="owner", cascade="all, delete-orphan")
    transactions = relationship("Transaction", foreign_keys="[Transaction.user_id]", back_populates="user", cascade="all, delete-orphan")
    logs = relationship("Log", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    @property
    def is_banned(self) -> bool:
        """Check if user is currently banned"""
        if self.status != UserStatus.BANNED:
            return False
        
        # Permanent ban
        if self.ban_until is None:
            return True
        
        # Temporary ban - check if expired
        return datetime.utcnow() < self.ban_until
    
    @property
    def can_create_vm(self) -> bool:
        """Check if user can create VMs"""
        return self.status == UserStatus.ACTIVE and not self.is_banned
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
