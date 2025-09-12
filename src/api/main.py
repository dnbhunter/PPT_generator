"""Main API router for DNB Presentation Generator."""

from fastapi import APIRouter

from .routes import (
    health,
    auth,
    presentations,
    generation,
    assets,
    admin,
)


# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["authentication"]
)

api_router.include_router(
    presentations.router,
    prefix="/presentations",
    tags=["presentations"]
)

api_router.include_router(
    generation.router,
    prefix="/generate",
    tags=["generation"]
)

api_router.include_router(
    assets.router,
    prefix="/assets",
    tags=["assets"]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["administration"]
)
