"""
Routes Package - تجميع نقاط النهاية
ملاحظة: هذه الملفات جاهزة للاستخدام عند استبدال server.py
حالياً، server.py يحتوي على جميع الـ APIs
"""
from fastapi import APIRouter

# Import all route modules (ready for future migration)
from .auth import router as auth_router
from .users import router as users_router
from .hr import router as hr_router
from .branches import router as branches_router
from .products import router as products_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all routers
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(hr_router)
api_router.include_router(branches_router)
api_router.include_router(products_router)

__all__ = ["api_router"]
