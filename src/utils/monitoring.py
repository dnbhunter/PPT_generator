"""Mock monitoring utilities for development."""

import asyncio
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


async def init_monitoring():
    """Initialize monitoring services."""
    await asyncio.sleep(0.1)
    logger.info("Monitoring initialized successfully")


class MockMonitoring:
    """Mock monitoring for development."""
    
    @staticmethod
    def track_event(event_name: str, properties: Optional[Dict[str, Any]] = None):
        """Track an event."""
        properties = properties or {}
        logger.info(f"Event tracked: {event_name} with properties: {properties}")
    
    @staticmethod
    def track_metric(metric_name: str, value: float, properties: Optional[Dict[str, Any]] = None):
        """Track a metric."""
        properties = properties or {}
        logger.info(f"Metric tracked: {metric_name} = {value} with properties: {properties}")


def get_monitoring():
    """Get monitoring instance."""
    return MockMonitoring()
