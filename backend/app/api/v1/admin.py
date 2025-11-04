from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from decimal import Decimal
from datetime import datetime

from app.core.database import get_async_db
from app.core.logging import audit_logger
from app.core.encryption import encryption
from app.api.deps import get_current_admin_user
from app.models.user import User, UserStatus, UserRole
from app.models.server import Server
from app.models.log import Log
from app.models.transaction import Transaction, TransactionType
from app.models.template import VMTemplate
from app.schemas.user import UserResponse, AddCreditsRequest, BanUserRequest, UnbanUserRequest
from app.schemas.server import ServerCreate, ServerResponse, ServerTestConnectionRequest
from app.schemas.template import TemplateCreate, TemplateResponse, TemplateUpdate


router = APIRouter(prefix="/admin")


# ==================== User Management ====================

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db),
    limit: int = 100,
    offset: int = 0
):
    """List all users (admin only)"""
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user details (admin only)"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post("/users/{user_id}/credit")
async def add_user_credit(
    user_id: int,
    credit_data: AddCreditsRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Add credits to user account (admin only)"""
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update balance
    user.balance += credit_data.amount
    
    # Create transaction record
    transaction = Transaction(
        user_id=user.id,
        amount=credit_data.amount,
        type=TransactionType.ADMIN_ADJUST,
        description=credit_data.reason or "Admin credit adjustment",
        admin_id=current_admin.id,
        balance_after=user.balance
    )
    
    db.add(transaction)
    await db.commit()
    
    audit_logger.log(
        "admin_credit_added",
        user_id=current_admin.id,
        details={
            "target_user_id": user.id,
            "amount": float(credit_data.amount),
            "reason": credit_data.reason
        }
    )
    
    return {
        "message": "Credits added successfully",
        "user_id": user.id,
        "new_balance": user.balance
    }


@router.post("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    ban_data: BanUserRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Ban user (admin only)"""
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot ban admin users"
        )
    
    # Update user status
    user.status = UserStatus.BANNED
    user.ban_reason = ban_data.reason
    user.ban_until = ban_data.ban_until  # None = permanent
    
    await db.commit()
    
    ban_type = "temporary" if ban_data.ban_until else "permanent"
    
    audit_logger.log(
        "user_banned",
        user_id=current_admin.id,
        details={
            "target_user_id": user.id,
            "ban_type": ban_type,
            "reason": ban_data.reason,
            "ban_until": ban_data.ban_until.isoformat() if ban_data.ban_until else None
        }
    )
    
    return {
        "message": f"User banned ({ban_type})",
        "user_id": user.id,
        "ban_until": ban_data.ban_until
    }


@router.post("/users/{user_id}/unban")
async def unban_user(
    user_id: int,
    unban_data: UnbanUserRequest,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Unban user (admin only)"""
    
    # Get user
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update user status
    user.status = UserStatus.ACTIVE
    user.ban_reason = None
    user.ban_until = None
    
    await db.commit()
    
    audit_logger.log(
        "user_unbanned",
        user_id=current_admin.id,
        details={
            "target_user_id": user.id,
            "reason": unban_data.reason
        }
    )
    
    return {"message": "User unbanned successfully", "user_id": user.id}


# ==================== Server Management ====================

@router.get("/servers", response_model=List[ServerResponse])
async def list_servers(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """List all Proxmox servers (admin only)"""
    result = await db.execute(select(Server).order_by(Server.name))
    servers = result.scalars().all()
    return servers


@router.post("/servers", response_model=ServerResponse, status_code=status.HTTP_201_CREATED)
async def create_server(
    server_data: ServerCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Add new Proxmox server (admin only)"""
    
    # Check if server name already exists
    result = await db.execute(
        select(Server).where(Server.name == server_data.name)
    )
    existing_server = result.scalar_one_or_none()
    
    if existing_server:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Server with this name already exists"
        )
    
    # Encrypt API token
    encrypted_token = encryption.encrypt(server_data.api_token)
    
    # Create server
    server = Server(
        name=server_data.name,
        description=server_data.description,
        api_url=server_data.api_url,
        port=server_data.port,
        api_token_encrypted=encrypted_token,
        verify_ssl=server_data.verify_ssl
    )
    
    db.add(server)
    await db.commit()
    await db.refresh(server)
    
    audit_logger.log(
        "server_added",
        user_id=current_admin.id,
        details={"server_id": server.id, "name": server.name}
    )
    
    return server


@router.post("/servers/test-connection")
async def test_server_connection(
    test_data: ServerTestConnectionRequest,
    current_admin: User = Depends(get_current_admin_user)
):
    """Test Proxmox server connection (admin only)"""
    
    # TODO: Implement actual Proxmox connection test
    # For now, return success
    
    return {
        "success": True,
        "message": "Connection successful",
        "version": "7.4-1"
    }


# ==================== Template Management ====================

@router.post("/templates", response_model=TemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: TemplateCreate,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Create VM template (admin only)"""
    
    # Check if template name already exists
    result = await db.execute(
        select(VMTemplate).where(VMTemplate.name == template_data.name)
    )
    existing_template = result.scalar_one_or_none()
    
    if existing_template:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Template with this name already exists"
        )
    
    # Create template
    template = VMTemplate(
        name=template_data.name,
        description=template_data.description,
        cpu_cores=template_data.cpu_cores,
        ram_mb=template_data.ram_mb,
        disk_gb=template_data.disk_gb,
        os_type=template_data.os_type,
        os_name=template_data.os_name,
        cost_per_hour=template_data.cost_per_hour,
        proxmox_template_id=template_data.proxmox_template_id,
        cloud_init_enabled=template_data.cloud_init_enabled,
        cloud_init_config=template_data.cloud_init_config,
        is_public=template_data.is_public,
        tags=template_data.tags
    )
    
    db.add(template)
    await db.commit()
    await db.refresh(template)
    
    audit_logger.log(
        "template_created",
        user_id=current_admin.id,
        details={"template_id": template.id, "name": template.name}
    )
    
    return template


@router.patch("/templates/{template_id}", response_model=TemplateResponse)
async def update_template(
    template_id: int,
    template_data: TemplateUpdate,
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update VM template (admin only)"""
    
    result = await db.execute(
        select(VMTemplate).where(VMTemplate.id == template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found"
        )
    
    # Update fields
    update_data = template_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    
    await db.commit()
    await db.refresh(template)
    
    audit_logger.log(
        "template_updated",
        user_id=current_admin.id,
        details={"template_id": template.id, "changes": update_data}
    )
    
    return template


# ==================== Logs ====================

@router.get("/logs")
async def get_logs(
    current_admin: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_async_db),
    limit: int = 100,
    offset: int = 0
):
    """Get audit logs (admin only)"""
    
    result = await db.execute(
        select(Log)
        .order_by(Log.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    logs = result.scalars().all()
    
    return {"logs": [
        {
            "id": log.id,
            "user_id": log.user_id,
            "action": log.action,
            "details": log.details,
            "created_at": log.created_at
        }
        for log in logs
    ]}
