from sqlalchemy import Column, Integer, String, DateTime, Numeric, Boolean, Text
from sqlalchemy.sql import func
from app.core.database import Base


class VMTemplate(Base):
    """VM Template model"""
    __tablename__ = "vm_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Resources
    cpu_cores = Column(Integer, nullable=False)
    ram_mb = Column(Integer, nullable=False)
    disk_gb = Column(Integer, nullable=False)
    
    # OS & Configuration
    os_type = Column(String(50), nullable=False)  # linux, windows
    os_name = Column(String(100), nullable=False)  # Ubuntu 22.04, Windows Server 2022
    
    # Proxmox template reference
    proxmox_template_id = Column(Integer, nullable=True)
    
    # Cloud-init configuration
    cloud_init_enabled = Column(Boolean, default=True)
    cloud_init_config = Column(Text, nullable=True)  # YAML config
    
    # Pricing
    cost_per_hour = Column(Numeric(10, 4), nullable=False)
    
    # Availability
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Visible to all users
    
    # Limits
    min_cpu = Column(Integer, default=1)
    max_cpu = Column(Integer, default=8)
    min_ram_mb = Column(Integer, default=512)
    max_ram_mb = Column(Integer, default=32768)
    min_disk_gb = Column(Integer, default=10)
    max_disk_gb = Column(Integer, default=500)
    
    # Metadata
    tags = Column(String(500), nullable=True)  # Comma-separated
    icon = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<VMTemplate(id={self.id}, name={self.name}, cost={self.cost_per_hour}/h)>"
    
    @property
    def cost_per_day(self) -> float:
        """Calculate cost per day"""
        return float(self.cost_per_hour) * 24
    
    @property
    def cost_per_month(self) -> float:
        """Calculate approximate cost per month (30 days)"""
        return float(self.cost_per_hour) * 24 * 30
