from decimal import Decimal
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.vm import VM, VMState
from app.models.transaction import Transaction, TransactionType
from app.models.template import VMTemplate
from app.core.logging import logger


class BillingService:
    """Service for handling billing operations"""
    
    @staticmethod
    async def calculate_vm_cost(
        vm: VM,
        template: VMTemplate,
        hours: float
    ) -> Decimal:
        """Calculate cost for VM usage"""
        return Decimal(str(template.cost_per_hour)) * Decimal(str(hours))
    
    @staticmethod
    async def bill_vm_usage(
        vm: VM,
        user: User,
        template: VMTemplate,
        db: AsyncSession
    ) -> Optional[Transaction]:
        """
        Bill user for VM usage since last billing
        Returns transaction if billing occurred, None otherwise
        """
        
        # Only bill if VM is in billable state
        if not vm.is_billable:
            return None
        
        # Calculate hours since last billing
        hours = vm.uptime_hours
        
        if hours <= 0:
            return None
        
        # Calculate cost
        cost = await BillingService.calculate_vm_cost(vm, template, hours)
        
        if cost <= 0:
            return None
        
        # Deduct from user balance
        user.balance -= cost
        
        # Create transaction
        transaction = Transaction(
            user_id=user.id,
            vm_id=vm.id,
            amount=-cost,  # Negative for debit
            type=TransactionType.DEBIT,
            description=f"VM usage: {vm.name} ({hours:.2f} hours)",
            balance_after=user.balance,
            transaction_metadata={
                "vm_id": vm.id,
                "hours": hours,
                "rate": float(template.cost_per_hour)
            }
        )
        
        db.add(transaction)
        
        # Update VM billing timestamp
        vm.last_billed_at = datetime.utcnow()
        vm.total_cost += int(cost * 100)  # Store in cents
        
        logger.info(f"Billed VM {vm.id} for {hours:.2f} hours: ${cost}")
        
        return transaction
    
    @staticmethod
    async def check_and_enforce_balance(
        user: User,
        db: AsyncSession,
        auto_shutdown: bool = True
    ) -> dict:
        """
        Check user balance and enforce policies
        Returns dict with actions taken
        """
        actions = {
            "warnings": [],
            "vms_stopped": [],
            "user_suspended": False
        }
        
        # If balance is low but positive, warn
        if 0 < user.balance < Decimal("10.00"):
            actions["warnings"].append("Low balance warning")
        
        # If balance is zero or negative
        if user.balance <= 0:
            if auto_shutdown:
                # Get all running VMs for this user
                result = await db.execute(
                    select(VM)
                    .where(VM.user_id == user.id)
                    .where(VM.state == VMState.RUNNING)
                )
                running_vms = result.scalars().all()
                
                for vm in running_vms:
                    # TODO: Stop VM via Proxmox API
                    vm.state = VMState.STOPPED
                    actions["vms_stopped"].append(vm.id)
                    logger.info(f"Auto-stopped VM {vm.id} due to insufficient balance")
        
        return actions
    
    @staticmethod
    async def add_credits(
        user: User,
        amount: Decimal,
        admin_id: Optional[int],
        reason: str,
        db: AsyncSession
    ) -> Transaction:
        """Add credits to user account"""
        
        # Update balance
        user.balance += amount
        
        # Create transaction
        transaction = Transaction(
            user_id=user.id,
            amount=amount,
            type=TransactionType.CREDIT if not admin_id else TransactionType.ADMIN_ADJUST,
            description=reason,
            admin_id=admin_id,
            balance_after=user.balance
        )
        
        db.add(transaction)
        
        logger.info(f"Added {amount} credits to user {user.id}")
        
        return transaction
