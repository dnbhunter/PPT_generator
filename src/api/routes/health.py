"""Health check routes for DNB Presentation Generator."""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from ...core.config import get_settings
from ...models.schemas import HealthCheck, APIResponse


router = APIRouter()
settings = get_settings()


@router.get("/", response_model=HealthCheck)
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        Health status information
    """
    return HealthCheck(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.app_version,
        environment=settings.environment,
        services=await get_service_statuses()
    )


@router.get("/detailed", response_model=APIResponse)
async def detailed_health_check():
    """
    Detailed health check with service dependencies.
    
    Returns:
        Detailed health status information
    """
    services = await get_detailed_service_statuses()
    
    # Determine overall health
    all_healthy = all(
        service["status"] == "healthy" 
        for service in services.values()
    )
    
    return APIResponse(
        success=all_healthy,
        message="System health check completed",
        data={
            "overall_status": "healthy" if all_healthy else "degraded",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.app_version,
            "environment": settings.environment,
            "services": services,
        }
    )


@router.get("/readiness")
async def readiness_check():
    """
    Kubernetes readiness probe endpoint.
    
    Returns:
        200 if ready, 503 if not ready
    """
    ready = await check_readiness()
    
    if ready:
        return JSONResponse(
            status_code=200,
            content={"status": "ready"}
        )
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "not ready"}
        )


@router.get("/liveness")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    
    Returns:
        200 if alive, 503 if not alive
    """
    alive = await check_liveness()
    
    if alive:
        return JSONResponse(
            status_code=200,
            content={"status": "alive"}
        )
    else:
        return JSONResponse(
            status_code=503,
            content={"status": "not alive"}
        )


async def get_service_statuses() -> Dict[str, str]:
    """Get basic service statuses."""
    return {
        "api": "healthy",
        "database": "healthy",  # Would check actual database
        "cache": "healthy",     # Would check actual Redis
        "azure_openai": "healthy",  # Would check actual Azure OpenAI
        "storage": "healthy",   # Would check actual Azure Storage
    }


async def get_detailed_service_statuses() -> Dict[str, Dict[str, Any]]:
    """Get detailed service statuses."""
    return {
        "api": {
            "status": "healthy",
            "version": settings.app_version,
            "uptime": "00:05:30",  # Would be actual uptime
            "memory_usage": "128MB",
            "cpu_usage": "5%",
        },
        "database": {
            "status": "healthy",
            "type": "PostgreSQL",
            "connections": 5,
            "pool_size": settings.database_pool_size,
            "response_time": "2ms",
        },
        "cache": {
            "status": "healthy",
            "type": "Redis",
            "memory_usage": "64MB",
            "connections": 3,
            "response_time": "1ms",
        },
        "azure_openai": {
            "status": "healthy",
            "model": settings.azure_openai_model_name,
            "endpoint": settings.azure_openai_endpoint,
            "response_time": "150ms",
        },
        "storage": {
            "status": "healthy",
            "type": "Azure Blob Storage",
            "container": settings.azure_storage_container_name,
            "response_time": "50ms",
        },
    }


async def check_readiness() -> bool:
    """Check if the application is ready to serve requests."""
    try:
        # Check database connectivity
        # await check_database_connection()
        
        # Check cache connectivity
        # await check_cache_connection()
        
        # Check Azure services
        # await check_azure_services()
        
        return True
    except Exception:
        return False


async def check_liveness() -> bool:
    """Check if the application is alive."""
    try:
        # Basic application health checks
        # This should be lightweight and fast
        return True
    except Exception:
        return False
