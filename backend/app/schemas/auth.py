from pydantic import BaseModel, EmailStr
from typing import Optional


class UserRegister(BaseModel):
    """User registration schema"""
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None


class UserLogin(BaseModel):
    """User login schema"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Token refresh request"""
    refresh_token: str


class PasswordReset(BaseModel):
    """Password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Password reset confirmation"""
    token: str
    new_password: str
