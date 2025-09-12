"""Authentication middleware for DNB Presentation Generator."""

import logging
from typing import Callable, List, Optional
from fastapi import Request, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for API requests."""
    
    def __init__(self, app, skip_paths: Optional[List[str]] = None):
        super().__init__(app)
        self.skip_paths = skip_paths or ["/", "/health", "/docs", "/openapi.json", "/redoc"]
        self.security = HTTPBearer(auto_error=False)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process authentication for incoming requests."""
        
        # Skip authentication for certain paths
        if request.url.path in self.skip_paths or request.url.path.startswith("/health"):
            return await call_next(request)
        
        # For development, allow requests without authentication
        # In production, this would validate Azure AD tokens
        logger.info(f"Request to {request.url.path} - Auth middleware (development mode)")
        
        # Add mock user to request state for development
        request.state.user = {
            "id": "dev-user-123",
            "email": "developer@dnb.no",
            "name": "Development User",
            "roles": ["creator", "admin"]
        }
        
        response = await call_next(request)
        return response
