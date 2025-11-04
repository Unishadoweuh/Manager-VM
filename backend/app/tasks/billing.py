from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.config import settings
from app.core.logging import logger
from app.models.user import User, UserStatus
from app.models.vm import VM, VMState
from app.models.template import VMTemplate
from app.services.billing import BillingService
from sqlalchemy import select
from datetime import datetime


@celery_app.task(name="app.tasks.billing.process_vm_billing")
def process_vm_billing():
    """Process billing for all running VMs"""
    
    if not settings.ENABLE_AUTO_BILLING:
        logger.info("Auto-billing is disabled, skipping")
        return {"status": "skipped", "reason": "auto_billing_disabled"}
    
    logger.info("Starting VM billing cycle")
    
    db = SessionLocal()
    billed_count = 0
    total_amount = 0
    
    try:
        # Get all billable VMs (running or suspended)
        result = db.execute(
            select(VM)
            .where(VM.state.in_([VMState.RUNNING, VMState.SUSPENDED]))
        )
        vms = result.scalars().all()
        
        logger.info(f"Found {len(vms)} billable VMs")
        
        for vm in vms:
            try:
                # Get user
                user = db.query(User).filter(User.id == vm.user_id).first()
                if not user:
                    logger.error(f"User {vm.user_id} not found for VM {vm.id}")
                    continue
                
                # Get template
                template = db.query(VMTemplate).filter(VMTemplate.id == vm.template_id).first()
                if not template:
                    logger.error(f"Template {vm.template_id} not found for VM {vm.id}")
                    continue
                
                # Bill the VM (synchronous version)
                hours = vm.uptime_hours
                if hours > 0:
                    cost = float(template.cost_per_hour) * hours
                    
                    # Update user balance
                    user.balance -= cost
                    
                    # Update VM
                    vm.last_billed_at = datetime.utcnow()
                    vm.total_cost += int(cost * 100)
                    
                    billed_count += 1
                    total_amount += cost
                    
                    logger.info(f"Billed VM {vm.id}: {hours:.2f}h * ${template.cost_per_hour} = ${cost:.2f}")
            
            except Exception as e:
                logger.error(f"Error billing VM {vm.id}: {e}")
                continue
        
        db.commit()
        
        logger.info(f"Billing cycle complete: {billed_count} VMs billed for ${total_amount:.2f}")
        
        return {
            "status": "success",
            "vms_billed": billed_count,
            "total_amount": total_amount
        }
    
    except Exception as e:
        logger.error(f"Error in billing cycle: {e}")
        db.rollback()
        return {
            "status": "error",
            "error": str(e)
        }
    
    finally:
        db.close()


@celery_app.task(name="app.tasks.billing.check_user_balances")
def check_user_balances():
    """Check user balances and enforce policies"""
    
    if not settings.ENABLE_AUTO_SHUTDOWN:
        logger.info("Auto-shutdown is disabled, skipping")
        return {"status": "skipped", "reason": "auto_shutdown_disabled"}
    
    logger.info("Checking user balances")
    
    db = SessionLocal()
    users_affected = 0
    vms_stopped = 0
    
    try:
        # Get users with zero or negative balance
        result = db.execute(
            select(User)
            .where(User.balance <= 0)
            .where(User.status == UserStatus.ACTIVE)
        )
        users = result.scalars().all()
        
        logger.info(f"Found {len(users)} users with insufficient balance")
        
        for user in users:
            try:
                # Get running VMs for this user
                result = db.execute(
                    select(VM)
                    .where(VM.user_id == user.id)
                    .where(VM.state == VMState.RUNNING)
                )
                running_vms = result.scalars().all()
                
                if running_vms:
                    users_affected += 1
                    
                    for vm in running_vms:
                        # Stop the VM
                        vm.state = VMState.STOPPED
                        vms_stopped += 1
                        logger.info(f"Auto-stopped VM {vm.id} for user {user.id} (balance: ${user.balance})")
            
            except Exception as e:
                logger.error(f"Error processing user {user.id}: {e}")
                continue
        
        db.commit()
        
        logger.info(f"Balance check complete: {vms_stopped} VMs stopped for {users_affected} users")
        
        return {
            "status": "success",
            "users_affected": users_affected,
            "vms_stopped": vms_stopped
        }
    
    except Exception as e:
        logger.error(f"Error checking balances: {e}")
        db.rollback()
        return {
            "status": "error",
            "error": str(e)
        }
    
    finally:
        db.close()
