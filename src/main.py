"""Main application entry point for DNB Presentation Generator."""

import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .core.config import get_settings, get_cors_config
from .core.exceptions import DNBPresentationError, EXCEPTION_STATUS_CODES
from .core.logging import setup_logging
from .api.main import api_router
from .api.middleware.auth import AuthMiddleware
from .api.middleware.audit import AuditMiddleware
from .api.middleware.security import SecurityMiddleware
from .api.middleware.rate_limiting import RateLimitMiddleware


# Get settings
settings = get_settings()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager."""
    # Startup
    logger.info("Starting DNB Presentation Generator")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize services
    try:
        await initialize_services()
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        sys.exit(1)
    
    yield
    
    # Shutdown
    logger.info("Shutting down DNB Presentation Generator")
    await cleanup_services()


async def initialize_services():
    """Initialize application services."""
    # Initialize database connections
    from .services.database import init_database
    await init_database()
    
    # Initialize cache
    from .services.cache_service import init_cache
    await init_cache()
    
    # Initialize monitoring
    from .utils.monitoring import init_monitoring
    await init_monitoring()
    
    # Initialize agents
    from .agents.orchestrator import MultiAgentOrchestrator
    app.state.orchestrator = MultiAgentOrchestrator()
    
    logger.info("Core services initialized")


async def cleanup_services():
    """Cleanup application services."""
    # Close database connections
    from .services.database import close_database
    await close_database()
    
    # Close cache connections
    from .services.cache_service import close_cache
    await close_cache()
    
    logger.info("Services cleanup completed")


def create_application() -> FastAPI:
    """Create FastAPI application with all configurations."""
    
    # Create FastAPI instance
    app = FastAPI(
        title="DNB Presentation Generator API",
        description="Enterprise text-to-presentation generator for DNB Bank",
        version=settings.app_version,
        environment=settings.environment,
        debug=settings.debug,
        lifespan=lifespan,
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        openapi_url="/openapi.json" if not settings.is_production else None,
    )
    
    # Configure CORS
    cors_config = get_cors_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
    )
    
    # Add security middleware
    app.add_middleware(SecurityMiddleware)
    
    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)
    
    # Add audit middleware
    app.add_middleware(AuditMiddleware)
    
    # Add authentication middleware
    app.add_middleware(AuthMiddleware)
    
    # Add trusted host middleware for production
    if settings.is_production:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.dnb.no", "localhost"]
        )
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    # Mount static files for frontend
    frontend_path = Path(__file__).parent.parent / "frontend"
    if frontend_path.exists():
        app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")
    
    # Add exception handlers
    add_exception_handlers(app)
    
    # Add startup event handlers
    add_event_handlers(app)
    
    return app


def add_exception_handlers(app: FastAPI):
    """Add custom exception handlers."""
    
    @app.exception_handler(DNBPresentationError)
    async def dnb_exception_handler(request, exc: DNBPresentationError):
        """Handle DNB specific exceptions."""
        status_code = EXCEPTION_STATUS_CODES.get(type(exc), 500)
        
        logger.error(
            f"DNB Exception: {exc.message}",
            extra={
                "error_code": exc.error_code,
                "details": exc.details,
                "status_code": status_code,
            }
        )
        
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "message": exc.message,
                "error_code": exc.error_code,
                "details": exc.details if settings.debug else {},
            }
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc: HTTPException):
        """Handle HTTP exceptions."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "error_code": f"HTTP_{exc.status_code}",
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """Handle general exceptions."""
        logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error" if settings.is_production else str(exc),
                "error_code": "INTERNAL_SERVER_ERROR",
            }
        )


def add_event_handlers(app: FastAPI):
    """Add event handlers."""
    
    @app.on_event("startup")
    async def startup_event():
        """Startup event handler."""
        logger.info("Application startup event triggered")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Shutdown event handler."""
        logger.info("Application shutdown event triggered")


# Create the application instance
app = create_application()


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "dnb-presentation-generator",
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": "2024-01-01T00:00:00Z",  # Would be actual timestamp
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "DNB Presentation Generator API",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs_url": "/docs" if not settings.is_production else None,
    }


def main():
    """Main function to run the application."""
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.worker_processes,
        log_level=settings.log_level.lower(),
        access_log=True,
        server_header=False,
        date_header=False,
    )


if __name__ == "__main__":
    main()
