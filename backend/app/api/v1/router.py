"""
Router principal de API v1.
Registra todos los endpoints de la aplicación.
"""
from fastapi import APIRouter

from app.api.v1 import (
    auth,
    restaurants,
    categories,
    dishes,
    menu,
    qr,
    upload,
    analytics
)

api_router = APIRouter()


# Routers activos
api_router.include_router(auth.router)           
api_router.include_router(restaurants.router)    # Restaurant CRUD
api_router.include_router(categories.router)     # Category CRUD
# api_router.include_router(dishes.router)         # Dish CRUD
api_router.include_router(menu.router)           # Public menu
api_router.include_router(qr.router)              # QR generation (GET /api/v1/admin/qr)
# api_router.include_router(upload.router)         # Image upload
# api_router.include_router(analytics.router)      # Analytics
