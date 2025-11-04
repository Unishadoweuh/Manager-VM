from cryptography.fernet import Fernet
import base64
from app.core.config import settings


class Encryption:
    """Encryption utilities for sensitive data"""
    
    def __init__(self):
        # Ensure the key is properly formatted
        key = settings.ENCRYPTION_KEY.encode() if isinstance(settings.ENCRYPTION_KEY, str) else settings.ENCRYPTION_KEY
        self.fernet = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string"""
        if not data:
            return ""
        encrypted = self.fernet.encrypt(data.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string"""
        if not encrypted_data:
            return ""
        decoded = base64.b64decode(encrypted_data.encode())
        decrypted = self.fernet.decrypt(decoded)
        return decrypted.decode()


# Global encryption instance
encryption = Encryption()
