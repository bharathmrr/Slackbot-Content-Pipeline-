"""
Redis cache management using Upstash Redis.
"""

import json
import asyncio
from typing import Any, Optional, Union
import redis
from loguru import logger

from app.config import get_settings


class CacheManager:
    """Manages Redis cache operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.client: Optional[redis.Redis] = None
        self._initialized = False
    
    def initialize(self):
        """Initialize Redis connection."""
        try:
            if not self.settings.redis_url:
                logger.warning("Redis URL not configured, caching will be disabled")
                return
            
            self.client = redis.from_url(
                self.settings.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.client.ping()
            
            self._initialized = True
            logger.info("Redis cache initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
            self.client = None
    
    async def health_check(self) -> bool:
        """Check cache health."""
        try:
            if not self._initialized or not self.client:
                return False
            
            self.client.ping()
            return True
            
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return False
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set a value in cache with TTL."""
        try:
            if not self.client:
                return False
            
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            result = self.client.setex(key, ttl, serialized_value)
            return result is True
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    def set_sync(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Synchronous version of set for Flask."""
        try:
            if not self.client:
                return False
            
            serialized_value = json.dumps(value) if not isinstance(value, str) else value
            result = self.client.setex(key, ttl, serialized_value)
            return result is True
            
        except Exception as e:
            logger.error(f"Error setting cache key {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from cache."""
        try:
            if not self.client:
                return None
            
            value = self.client.get(key)
            if value is None:
                return None
            
            # Try to deserialize JSON, fallback to string
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    def get_sync(self, key: str) -> Optional[Any]:
        """Synchronous version of get for Flask."""
        try:
            if not self.client:
                return None
            
            value = self.client.get(key)
            if value is None:
                return None
            
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
                
        except Exception as e:
            logger.error(f"Error getting cache key {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        try:
            if not self.client:
                return False
            
            result = self.client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    def delete_sync(self, key: str) -> bool:
        """Synchronous version of delete for Flask."""
        try:
            if not self.client:
                return False
            
            result = self.client.delete(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Error deleting cache key {key}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in cache."""
        try:
            if not self.client:
                return False
            
            result = self.client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    def exists_sync(self, key: str) -> bool:
        """Synchronous version of exists for Flask."""
        try:
            if not self.client:
                return False
            
            result = self.client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.error(f"Error checking cache key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value in cache."""
        try:
            if not self.client:
                return 0
            
            result = self.client.incrby(key, amount)
            return result
            
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return 0
    
    def increment_sync(self, key: str, amount: int = 1) -> int:
        """Synchronous version of increment for Flask."""
        try:
            if not self.client:
                return 0
            
            result = self.client.incrby(key, amount)
            return result
            
        except Exception as e:
            logger.error(f"Error incrementing cache key {key}: {e}")
            return 0
    
    # Specialized cache methods
    async def cache_keyword_embeddings(self, keywords: list, embeddings: list) -> bool:
        """Cache keyword embeddings."""
        key = f"embeddings:{hash(tuple(keywords))}"
        return await self.set(key, embeddings, ttl=86400)  # 24 hours
    
    async def get_cached_keyword_embeddings(self, keywords: list) -> Optional[list]:
        """Get cached keyword embeddings."""
        key = f"embeddings:{hash(tuple(keywords))}"
        return await self.get(key)
    
    async def cache_web_content(self, url: str, content: dict) -> bool:
        """Cache web content."""
        key = f"webcontent:{hash(url)}"
        return await self.set(key, content, ttl=3600)  # 1 hour
    
    async def get_cached_web_content(self, url: str) -> Optional[dict]:
        """Get cached web content."""
        key = f"webcontent:{hash(url)}"
        return await self.get(key)
    
    async def cache_processing_status(self, batch_id: str, status: dict) -> bool:
        """Cache processing status."""
        key = f"processing:{batch_id}"
        return await self.set(key, status, ttl=1800)  # 30 minutes
    
    async def get_processing_status(self, batch_id: str) -> Optional[dict]:
        """Get processing status."""
        key = f"processing:{batch_id}"
        return await self.get(key)
    
    async def set_processing_lock(self, batch_id: str, ttl: int = 300) -> bool:
        """Set a processing lock."""
        key = f"lock:{batch_id}"
        try:
            if not self.client:
                return False
            
            # Use SET with NX (only if not exists) and EX (expiration)
            result = self.client.set(key, "1", nx=True, ex=ttl)
            return result is True
            
        except Exception as e:
            logger.error(f"Error setting processing lock {batch_id}: {e}")
            return False
    
    def set_processing_lock_sync(self, batch_id: str, ttl: int = 300) -> bool:
        """Synchronous version of set_processing_lock for Flask."""
        key = f"lock:{batch_id}"
        try:
            if not self.client:
                return False
            
            result = self.client.set(key, "1", nx=True, ex=ttl)
            return result is True
            
        except Exception as e:
            logger.error(f"Error setting processing lock {batch_id}: {e}")
            return False
    
    async def release_processing_lock(self, batch_id: str) -> bool:
        """Release a processing lock."""
        key = f"lock:{batch_id}"
        return await self.delete(key)
    
    def release_processing_lock_sync(self, batch_id: str) -> bool:
        """Synchronous version of release_processing_lock for Flask."""
        key = f"lock:{batch_id}"
        return self.delete_sync(key)
    
    async def close(self):
        """Close Redis connections."""
        try:
            if self.client:
                self.client.close()
            self._initialized = False
            logger.info("Redis cache connections closed")
            
        except Exception as e:
            logger.error(f"Error closing Redis cache: {e}")


# Cache key patterns for reference
CACHE_PATTERNS = {
    "embeddings": "embeddings:{hash}",
    "web_content": "webcontent:{hash}",
    "processing_status": "processing:{batch_id}",
    "processing_lock": "lock:{batch_id}",
    "rate_limit": "rate_limit:{user_id}",
    "search_results": "search:{query_hash}",
    "outlines": "outline:{group_id}",
    "post_ideas": "ideas:{group_id}"
}
