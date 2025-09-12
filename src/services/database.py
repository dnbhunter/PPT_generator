"""Mock database service for development."""

import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MockDatabase:
    """Mock database for development and testing."""
    
    def __init__(self):
        self.data = {}
        self.connected = False
    
    async def connect(self):
        """Mock database connection."""
        await asyncio.sleep(0.1)
        self.connected = True
        logger.info("Mock database connected")
    
    async def disconnect(self):
        """Mock database disconnection."""
        self.connected = False
        logger.info("Mock database disconnected")
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get data by key."""
        return self.data.get(key)
    
    async def set(self, key: str, value: Dict[str, Any]):
        """Set data by key."""
        self.data[key] = value
    
    async def delete(self, key: str):
        """Delete data by key."""
        self.data.pop(key, None)


# Global database instance
_database = MockDatabase()


async def init_database():
    """Initialize database connection."""
    try:
        await _database.connect()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_database():
    """Close database connection."""
    try:
        await _database.disconnect()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Failed to close database: {e}")


def get_database() -> MockDatabase:
    """Get database instance."""
    return _database
