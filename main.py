"""
DNB Presentation Generator - Main Application Entry Point
"""

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.config import settings, get_cors_config
from src.api.middleware.security import SecurityHeadersMiddleware
from src.api.middleware.auth import AuthenticationMiddleware  
from src.api.middleware.audit import AuditMiddleware
from src.api.middleware.rate_limiting import RateLimitingMiddleware
from src.api.routes import presentations, health, auth
from src.services.database import get_database_service
from src.services.cache_service import get_cache_service
from src.utils.monitoring import setup_monitoring


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle manager."""
    logger.info("Starting DNB Presentation Generator...")
    
    # Initialize services
    try:
        # Initialize database
        db_service = get_database_service()
        await db_service.initialize()
        logger.info("Database service initialized")
        
        # Initialize cache
        cache_service = get_cache_service()
        await cache_service.initialize()
        logger.info("Cache service initialized")
        
        # Setup monitoring
        setup_monitoring(app)
        logger.info("Monitoring initialized")
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Cleanup
    try:
        logger.info("Shutting down application...")
        
        # Close database connections
        if 'db_service' in locals():
            await db_service.close()
            
        # Close cache connections  
        if 'cache_service' in locals():
            await cache_service.close()
            
        logger.info("Application shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Enterprise presentation generation platform with AI-powered content creation",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
        lifespan=lifespan
    )
    
    # Configure CORS
    cors_config = get_cors_config()
    app.add_middleware(
        CORSMiddleware,
        **cors_config
    )
    
    # Add security middleware
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(AuthenticationMiddleware)
    app.add_middleware(AuditMiddleware)
    app.add_middleware(RateLimitingMiddleware)
    
    # Add trusted host middleware for production
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.allowed_origins_list
        )
    
    # Include routers
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
    app.include_router(presentations.router, prefix="/api/v1/presentations", tags=["presentations"])
    
    # Global exception handler
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.detail, "status_code": exc.status_code}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "status_code": 500}
        )
    
    return app


# Create the application instance
app = create_app()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "DNB Presentation Generator API",
        "version": settings.app_version,
        "status": "running",
        "environment": settings.environment,
        "docs_url": "/docs" if settings.debug else "disabled"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
