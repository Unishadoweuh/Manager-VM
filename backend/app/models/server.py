from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from app.core.database import Base


class ServerStatus(str, enum.Enum):
    """Proxmox server status"""
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class Server(Base):
    """Proxmox server model"""
    __tablename__ = "servers"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Server identification
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Connection details
    api_url = Column(String(255), nullable=False)  # https://proxmox.example.com:8006
    port = Column(Integer, default=8006)
    
    # Authentication (encrypted)
    api_token_encrypted = Column(Text, nullable=False)  # Encrypted API token
    
    # SSL verification
    verify_ssl = Column(Boolean, default=True)
    
    # Status
    status = Column(SQLEnum(ServerStatus), default=ServerStatus.OFFLINE, nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    last_error = Column(Text, nullable=True)
    
    # Capacity (updated periodically)
    total_cpu_cores = Column(Integer, default=0)
    used_cpu_cores = Column(Integer, default=0)
    total_ram_mb = Column(Integer, default=0)
    used_ram_mb = Column(Integer, default=0)
    total_disk_gb = Column(Integer, default=0)
    used_disk_gb = Column(Integer, default=0)
    
    # Settings
    is_active = Column(Boolean, default=True)
    allow_vm_creation = Column(Boolean, default=True)
    priority = Column(Integer, default=0)  # Higher = preferred for new VMs
    
    # Metadata
    datacenter = Column(String(100), nullable=True)
    location = Column(String(200), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Server(id={self.id}, name={self.name}, status={self.status})>"
    
    @property
    def is_available(self) -> bool:
        """Check if server is available for VM creation"""
        return (
            self.is_active and
            self.allow_vm_creation and
            self.status == ServerStatus.ONLINE
        )
    
    @property
    def cpu_usage_percent(self) -> float:
        """Calculate CPU usage percentage"""
        if self.total_cpu_cores == 0:
            return 0.0
        return (self.used_cpu_cores / self.total_cpu_cores) * 100
    
    @property
    def ram_usage_percent(self) -> float:
        """Calculate RAM usage percentage"""
        if self.total_ram_mb == 0:
            return 0.0
        return (self.used_ram_mb / self.total_ram_mb) * 100
    
    @property
    def disk_usage_percent(self) -> float:
        """Calculate disk usage percentage"""
        if self.total_disk_gb == 0:
            return 0.0
        return (self.used_disk_gb / self.total_disk_gb) * 100
