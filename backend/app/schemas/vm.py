from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class VMCreate(BaseModel):
    """Create VM request"""
    template_id: int
    name: str = Field(..., min_length=3, max_length=100)
    hostname: Optional[str] = None
    cpu_cores: Optional[int] = Field(None, ge=1, le=16)
    ram_mb: Optional[int] = Field(None, ge=512, le=65536)
    disk_gb: Optional[int] = Field(None, ge=10, le=1000)
    notes: Optional[str] = None


class VMUpdate(BaseModel):
    """Update VM request"""
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    notes: Optional[str] = None


class VMResize(BaseModel):
    """Resize VM request"""
    cpu_cores: Optional[int] = Field(None, ge=1, le=16)
    ram_mb: Optional[int] = Field(None, ge=512, le=65536)
    disk_gb: Optional[int] = Field(None, ge=10, le=1000)


class VMAction(BaseModel):
    """VM action request"""
    action: str = Field(..., pattern="^(start|stop|reboot|suspend|resume)$")


class VMResponse(BaseModel):
    """VM response"""
    id: int
    user_id: int
    template_id: int
    proxmox_vm_id: Optional[int]
    node_name: str
    name: str
    hostname: Optional[str]
    cpu_cores: int
    ram_mb: int
    disk_gb: int
    ip_address: Optional[str]
    state: str
    total_cost: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class VMListResponse(BaseModel):
    """VM list response"""
    vms: list[VMResponse]
    total: int
