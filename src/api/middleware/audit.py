"""Audit middleware for DNB Presentation Generator."""

import logging
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AuditMiddleware(BaseHTTPMiddleware):
    """Audit middleware for logging all API requests."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log audit information for requests."""
        
        start_time = time.time()
        
        # Extract request info
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        method = request.method
        path = request.url.path
        
        # Get user info from request state (set by auth middleware)
        user_id = getattr(request.state, "user", {}).get("id", "anonymous")
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log audit event
        logger.info(
            f"Audit: {method} {path} - User: {user_id} - IP: {client_ip} - "
            f"Status: {response.status_code} - Duration: {duration:.3f}s",
            extra={
                "audit_event": True,
                "method": method,
                "path": path,
                "user_id": user_id,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "status_code": response.status_code,
                "duration": duration
            }
        )
        
        return response
