import redis
from typing import Optional
from app.core.config import settings
from app.core.logging import logger


class RateLimiter:
    """Redis-based rate limiter for brute force protection"""
    
    def __init__(self):
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def is_rate_limited(self, key: str, max_attempts: int, window_seconds: int) -> bool:
        """
        Check if a key is rate limited
        
        Args:
            key: Unique identifier (e.g., IP address, username)
            max_attempts: Maximum allowed attempts
            window_seconds: Time window in seconds
        
        Returns:
            True if rate limited, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            current = self.redis_client.get(key)
            
            if current is None:
                self.redis_client.setex(key, window_seconds, 1)
                return False
            
            attempts = int(current)
            
            if attempts >= max_attempts:
                return True
            
            self.redis_client.incr(key)
            return False
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return False
    
    def reset_limit(self, key: str) -> None:
        """Reset rate limit for a key"""
        if not self.redis_client:
            return
        
        try:
            self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Rate limit reset failed: {e}")
    
    def get_remaining_attempts(self, key: str, max_attempts: int) -> int:
        """Get remaining attempts before rate limit"""
        if not self.redis_client:
            return max_attempts
        
        try:
            current = self.redis_client.get(key)
            if current is None:
                return max_attempts
            
            attempts = int(current)
            return max(0, max_attempts - attempts)
            
        except Exception as e:
            logger.error(f"Failed to get remaining attempts: {e}")
            return max_attempts


rate_limiter = RateLimiter()
