from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from app.core.database import get_async_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token_type
)
from app.core.rate_limit import rate_limiter
from app.core.config import settings
from app.core.logging import audit_logger
from app.models.user import User, UserRole, UserStatus
from app.schemas.auth import UserRegister, UserLogin, Token, TokenRefresh


router = APIRouter(prefix="/auth")


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_async_db)
):
    """Register a new user"""
    
    # Check if registration is enabled
    if not settings.ENABLE_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration is currently disabled"
        )
    
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        company=user_data.company,
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        balance=0.00
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    audit_logger.log("user_registered", user_id=user.id, details={"email": user.email})
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/login", response_model=Token)
async def login(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_async_db)
):
    """Login user"""
    
    # Rate limiting
    rate_limit_key = f"login:{credentials.email}"
    if rate_limiter.is_rate_limited(
        rate_limit_key,
        settings.RATE_LIMIT_LOGIN_ATTEMPTS,
        settings.RATE_LIMIT_LOGIN_WINDOW
    ):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    # Find user
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        audit_logger.log(
            "login_failed",
            details={"email": credentials.email},
            level="WARNING"
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Reset rate limit on successful login
    rate_limiter.reset_limit(rate_limit_key)
    
    # Update last login
    user.last_login = datetime.utcnow()
    await db.commit()
    
    audit_logger.log("user_logged_in", user_id=user.id)
    
    # Generate tokens
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=Token)
async def refresh(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_async_db)
):
    """Refresh access token"""
    
    payload = decode_token(token_data.refresh_token)
    verify_token_type(payload, "refresh")
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Verify user exists
    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new tokens
    access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token
    )
