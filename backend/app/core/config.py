from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Uni-Manager"
    VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str  # Base64 encoded 32-byte key for Fernet
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = []
    
    # Feature Flags
    ENABLE_PAYMENTS: bool = False
    ENABLE_AUTO_BILLING: bool = True
    ENABLE_AUTO_SHUTDOWN: bool = True
    ENABLE_REGISTRATION: bool = True
    
    # Payments
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    
    # Email
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    EMAILS_FROM_EMAIL: str = "noreply@unimanager.com"
    EMAILS_FROM_NAME: str = "Uni-Manager"
    
    # Rate Limiting
    RATE_LIMIT_LOGIN_ATTEMPTS: int = 5
    RATE_LIMIT_LOGIN_WINDOW: int = 300  # seconds
    
    # Billing
    BILLING_CYCLE_MINUTES: int = 60
    MIN_BALANCE_THRESHOLD: float = 0.0
    
    # Audit
    LOG_RETENTION_DAYS: int = 365
    
    # Admin
    FIRST_ADMIN_EMAIL: str = "admin@unimanager.com"
    FIRST_ADMIN_PASSWORD: str = "changeme"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == 'BACKEND_CORS_ORIGINS':
                return [i.strip() for i in raw_val.split(',')]
            return cls.json_loads(raw_val)


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
