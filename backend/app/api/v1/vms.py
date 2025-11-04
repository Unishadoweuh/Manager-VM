from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from decimal import Decimal
from datetime import datetime

from app.core.database import get_async_db
from app.core.logging import audit_logger
from app.core.config import settings
from app.api.deps import get_current_active_user
from app.models.user import User
from app.models.vm import VM, VMState
from app.models.template import VMTemplate
from app.models.transaction import Transaction, TransactionType
from app.models.server import Server, ServerStatus
from app.schemas.vm import VMCreate, VMResponse, VMAction, VMListResponse
from app.services.proxmox import ProxmoxService
from app.services.billing import BillingService


router = APIRouter(prefix="/vms")


@router.get("", response_model=VMListResponse)
async def list_vms(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """List user's VMs"""
    result = await db.execute(
        select(VM)
        .where(VM.user_id == current_user.id)
        .where(VM.state != VMState.DELETED)
        .order_by(VM.created_at.desc())
    )
    vms = result.scalars().all()
    
    return VMListResponse(vms=vms, total=len(vms))


@router.post("", response_model=VMResponse, status_code=status.HTTP_201_CREATED)
async def create_vm(
    vm_data: VMCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new VM from template"""
    
    # Check if user can create VMs
    if not current_user.can_create_vm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot create VMs. Account may be banned or suspended."
        )
    
    # Get template
    result = await db.execute(
        select(VMTemplate).where(VMTemplate.id == vm_data.template_id)
    )
    template = result.scalar_one_or_none()
    
    if not template or not template.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found or inactive"
        )
    
    # Use template defaults or user-specified values
    cpu_cores = vm_data.cpu_cores or template.cpu_cores
    ram_mb = vm_data.ram_mb or template.ram_mb
    disk_gb = vm_data.disk_gb or template.disk_gb
    
    # Calculate estimated cost for 1 hour
    estimated_cost = template.cost_per_hour
    
    # Check if user has sufficient balance
    if current_user.balance < estimated_cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient balance. Required: {estimated_cost}, Available: {current_user.balance}"
        )
    
    # Find available server
    result = await db.execute(
        select(Server)
        .where(Server.is_active == True)
        .where(Server.allow_vm_creation == True)
        .where(Server.status == ServerStatus.ONLINE)
        .order_by(Server.priority.desc())
        .limit(1)
    )
    server = result.scalar_one_or_none()
    
    if not server:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No available servers for VM creation"
        )
    
    # Create VM record
    vm = VM(
        user_id=current_user.id,
        template_id=template.id,
        server_id=server.id,
        name=vm_data.name,
        hostname=vm_data.hostname or vm_data.name,
        cpu_cores=cpu_cores,
        ram_mb=ram_mb,
        disk_gb=disk_gb,
        node_name=server.name,  # Will be updated with actual node
        state=VMState.CREATING,
        notes=vm_data.notes
    )
    
    db.add(vm)
    await db.commit()
    await db.refresh(vm)
    
    # TODO: Queue VM creation task via Celery
    # For now, mark as creating
    
    audit_logger.log(
        "vm_created",
        user_id=current_user.id,
        details={"vm_id": vm.id, "template_id": template.id, "name": vm.name}
    )
    
    return vm


@router.get("/{vm_id}", response_model=VMResponse)
async def get_vm(
    vm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get VM details"""
    result = await db.execute(
        select(VM)
        .where(VM.id == vm_id)
        .where(VM.user_id == current_user.id)
    )
    vm = result.scalar_one_or_none()
    
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found"
        )
    
    return vm


@router.post("/{vm_id}/action", response_model=dict)
async def vm_action(
    vm_id: int,
    action: VMAction,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Perform action on VM (start, stop, reboot, etc.)"""
    
    # Get VM
    result = await db.execute(
        select(VM)
        .where(VM.id == vm_id)
        .where(VM.user_id == current_user.id)
    )
    vm = result.scalar_one_or_none()
    
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found"
        )
    
    # Check if user can start VMs (for start action)
    if action.action == "start" and not current_user.can_create_vm:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot start VM. Account may be banned."
        )
    
    # Check balance for start action
    if action.action == "start" and current_user.balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient balance to start VM"
        )
    
    # TODO: Execute action via Proxmox service
    # For now, update state
    if action.action == "start":
        vm.state = VMState.RUNNING
        vm.last_billed_at = datetime.utcnow()
    elif action.action == "stop":
        vm.state = VMState.STOPPED
    elif action.action == "reboot":
        pass  # State remains running
    
    await db.commit()
    
    audit_logger.log(
        f"vm_{action.action}",
        user_id=current_user.id,
        details={"vm_id": vm.id, "action": action.action}
    )
    
    return {"message": f"VM {action.action} action initiated", "vm_id": vm.id}


@router.delete("/{vm_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vm(
    vm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete VM"""
    
    result = await db.execute(
        select(VM)
        .where(VM.id == vm_id)
        .where(VM.user_id == current_user.id)
    )
    vm = result.scalar_one_or_none()
    
    if not vm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="VM not found"
        )
    
    # Soft delete
    vm.state = VMState.DELETED
    vm.deleted_at = datetime.utcnow()
    
    await db.commit()
    
    audit_logger.log(
        "vm_deleted",
        user_id=current_user.id,
        details={"vm_id": vm.id}
    )
    
    return None
