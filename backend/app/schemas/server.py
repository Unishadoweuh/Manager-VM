from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ServerBase(BaseModel):
    """Base server schema"""
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    api_url: str
    port: int = 8006
    verify_ssl: bool = True


class ServerCreate(ServerBase):
    """Create server request"""
    api_token: str  # Will be encrypted before storage


class ServerUpdate(BaseModel):
    """Update server request"""
    name: Optional[str] = None
    description: Optional[str] = None
    api_url: Optional[str] = None
    api_token: Optional[str] = None
    verify_ssl: Optional[bool] = None
    is_active: Optional[bool] = None
    allow_vm_creation: Optional[bool] = None


class ServerResponse(ServerBase):
    """Server response"""
    id: int
    status: str
    last_seen_at: Optional[datetime]
    last_error: Optional[str]
    total_cpu_cores: int
    used_cpu_cores: int
    total_ram_mb: int
    used_ram_mb: int
    total_disk_gb: int
    used_disk_gb: int
    is_active: bool
    allow_vm_creation: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ServerTestConnectionRequest(BaseModel):
    """Test server connection request"""
    api_url: str
    api_token: str
    verify_ssl: bool = True
