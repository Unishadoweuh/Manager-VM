from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base


class VMState(str, enum.Enum):
    """VM states"""
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    SUSPENDED = "suspended"
    ERROR = "error"
    DELETING = "deleting"
    DELETED = "deleted"


class VM(Base):
    """Virtual Machine model"""
    __tablename__ = "user_vms"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Owner
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Template
    template_id = Column(Integer, ForeignKey("vm_templates.id"), nullable=False)
    
    # Proxmox identifiers
    proxmox_vm_id = Column(Integer, nullable=True)  # VMID in Proxmox
    node_name = Column(String(100), nullable=False)  # Proxmox node name
    server_id = Column(Integer, ForeignKey("servers.id"), nullable=False)
    
    # VM Configuration
    name = Column(String(100), nullable=False)
    hostname = Column(String(100), nullable=True)
    
    # Current resources (can be resized)
    cpu_cores = Column(Integer, nullable=False)
    ram_mb = Column(Integer, nullable=False)
    disk_gb = Column(Integer, nullable=False)
    
    # Network
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    mac_address = Column(String(17), nullable=True)
    
    # State
    state = Column(SQLEnum(VMState), default=VMState.CREATING, nullable=False, index=True)
    
    # Billing
    last_billed_at = Column(DateTime(timezone=True), nullable=True)
    total_cost = Column(Integer, default=0)  # Total credits consumed
    
    # Metadata
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="vms")
    template = relationship("VMTemplate")
    server = relationship("Server")
    
    def __repr__(self):
        return f"<VM(id={self.id}, name={self.name}, state={self.state}, user_id={self.user_id})>"
    
    @property
    def is_billable(self) -> bool:
        """Check if VM should be billed"""
        return self.state in [VMState.RUNNING, VMState.SUSPENDED]
    
    @property
    def uptime_hours(self) -> float:
        """Calculate uptime in hours since last billing"""
        if not self.last_billed_at:
            delta = datetime.utcnow() - self.created_at.replace(tzinfo=None)
        else:
            delta = datetime.utcnow() - self.last_billed_at.replace(tzinfo=None)
        
        return delta.total_seconds() / 3600
