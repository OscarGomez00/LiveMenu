from fastapi import APIRouter

from app.api.v1 import (
    auth,
    restaurants,
    categories,
    menu,
    qr,
    upload,
    analytics
)
from app.api.v1.admin.router import admin_router

api_router = APIRouter()

# Autenticación
api_router.include_router(auth.router)

# Rutas públicas
api_router.include_router(restaurants.router)
api_router.include_router(categories.router)
api_router.include_router(menu.router)
api_router.include_router(qr.router)
api_router.include_router(upload.router)          # Image upload (CU-05)
# api_router.include_router(analytics.router)    # Analytics (pendiente)

# Administración (incluye gestión de platos CU-04 y categorías admin)
api_router.include_router(admin_router)
