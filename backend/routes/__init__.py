"""
Routes Package - تجميع نقاط النهاية
"""
from fastapi import APIRouter

# Import all route modules
from .auth import router as auth_router
from .users import router as users_router
from .hr import router as hr_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(hr_router)

__all__ = ["api_router"]
