import logging
import sys
from typing import Any
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("unimanager")


class AuditLogger:
    """Audit logger for security-sensitive operations"""
    
    def __init__(self):
        self.logger = logging.getLogger("unimanager.audit")
        self.logger.setLevel(logging.INFO)
    
    def log(
        self,
        action: str,
        user_id: int = None,
        details: dict[str, Any] = None,
        level: str = "INFO"
    ):
        """Log an audit event"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details or {}
        }
        
        log_message = json.dumps(log_data)
        
        if level == "ERROR":
            self.logger.error(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)


audit_logger = AuditLogger()
