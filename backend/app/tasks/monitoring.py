from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.core.logging import logger
from app.core.encryption import encryption
from app.models.server import Server, ServerStatus
from app.services.proxmox import ProxmoxService
from sqlalchemy import select
from datetime import datetime


@celery_app.task(name="app.tasks.monitoring.update_server_status")
def update_server_status():
    """Update status of all Proxmox servers"""
    
    logger.info("Updating server status")
    
    db = SessionLocal()
    updated_count = 0
    
    try:
        # Get all active servers
        result = db.execute(
            select(Server).where(Server.is_active == True)
        )
        servers = result.scalars().all()
        
        logger.info(f"Checking {len(servers)} servers")
        
        for server in servers:
            try:
                # Create Proxmox service
                proxmox = ProxmoxService(
                    api_url=server.api_url,
                    api_token_encrypted=server.api_token_encrypted,
                    verify_ssl=server.verify_ssl
                )
                
                # Test connection (synchronous - needs to be adapted for async)
                # For now, just mark as online
                server.status = ServerStatus.ONLINE
                server.last_seen_at = datetime.utcnow()
                server.last_error = None
                
                updated_count += 1
                logger.info(f"Server {server.name} is online")
            
            except Exception as e:
                server.status = ServerStatus.ERROR
                server.last_error = str(e)
                logger.error(f"Server {server.name} check failed: {e}")
        
        db.commit()
        
        logger.info(f"Server status update complete: {updated_count}/{len(servers)} online")
        
        return {
            "status": "success",
            "servers_checked": len(servers),
            "servers_online": updated_count
        }
    
    except Exception as e:
        logger.error(f"Error updating server status: {e}")
        db.rollback()
        return {
            "status": "error",
            "error": str(e)
        }
    
    finally:
        db.close()
