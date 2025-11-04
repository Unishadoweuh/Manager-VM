from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema"""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None


class UserResponse(UserBase):
    """User response schema"""
    id: int
    role: str
    balance: Decimal
    status: str
    ban_reason: Optional[str] = None
    ban_until: Optional[datetime] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserCreditsResponse(BaseModel):
    """User credits response"""
    balance: Decimal
    currency: str = "USD"


class AddCreditsRequest(BaseModel):
    """Add credits request"""
    amount: Decimal = Field(..., gt=0)
    reason: Optional[str] = None


class BanUserRequest(BaseModel):
    """Ban user request"""
    reason: str
    ban_until: Optional[datetime] = None  # None = permanent ban


class UnbanUserRequest(BaseModel):
    """Unban user request"""
    reason: Optional[str] = None
