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

# Router principal
api_router = APIRouter()

# Incluir todos los routers
# Cada desarrollador debe incluir su router aquí cuando lo complete

# TODO: Descomentar conforme se implementen
# api_router.include_router(auth.router)           # Auth endpoints
api_router.include_router(restaurants.router)    # Restaurant CRUD
# api_router.include_router(categories.router)     # Category CRUD
# api_router.include_router(dishes.router)         # Dish CRUD
# api_router.include_router(menu.router)           # Public menu
# api_router.include_router(qr.router)             # QR generation
# api_router.include_router(upload.router)         # Image upload
# api_router.include_router(analytics.router)      # Analytics
