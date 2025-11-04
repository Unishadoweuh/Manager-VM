from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class TemplateBase(BaseModel):
    """Base template schema"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    cpu_cores: int = Field(..., ge=1, le=32)
    ram_mb: int = Field(..., ge=512, le=131072)
    disk_gb: int = Field(..., ge=10, le=2000)
    os_type: str = Field(..., pattern="^(linux|windows)$")
    os_name: str
    cost_per_hour: Decimal = Field(..., gt=0)


class TemplateCreate(TemplateBase):
    """Create template request"""
    proxmox_template_id: Optional[int] = None
    cloud_init_enabled: bool = True
    cloud_init_config: Optional[str] = None
    is_public: bool = True
    tags: Optional[str] = None


class TemplateUpdate(BaseModel):
    """Update template request"""
    name: Optional[str] = None
    description: Optional[str] = None
    cost_per_hour: Optional[Decimal] = Field(None, gt=0)
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class TemplateResponse(TemplateBase):
    """Template response"""
    id: int
    proxmox_template_id: Optional[int]
    cloud_init_enabled: bool
    is_active: bool
    is_public: bool
    tags: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    # Computed fields
    cost_per_day: Optional[Decimal] = None
    cost_per_month: Optional[Decimal] = None
    
    class Config:
        from_attributes = True
