"""Mock cache service for development."""

import asyncio
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class MockCache:
    """Mock cache for development and testing."""
    
    def __init__(self):
        self.data = {}
        self.connected = False
    
    async def connect(self):
        """Mock cache connection."""
        await asyncio.sleep(0.1)
        self.connected = True
        logger.info("Mock cache connected")
    
    async def disconnect(self):
        """Mock cache disconnection."""
        self.connected = False
        logger.info("Mock cache disconnected")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        return self.data.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        """Set cached value with TTL."""
        self.data[key] = value
    
    async def delete(self, key: str):
        """Delete cached value."""
        self.data.pop(key, None)
    
    async def clear(self):
        """Clear all cached values."""
        self.data.clear()


# Global cache instance
_cache = MockCache()


async def init_cache():
    """Initialize cache connection."""
    try:
        await _cache.connect()
        logger.info("Cache initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize cache: {e}")
        raise


async def close_cache():
    """Close cache connection."""
    try:
        await _cache.disconnect()
        logger.info("Cache connection closed")
    except Exception as e:
        logger.error(f"Failed to close cache: {e}")


def get_cache() -> MockCache:
    """Get cache instance."""
    return _cache
