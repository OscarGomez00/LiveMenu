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

# Router principal
api_router = APIRouter()

# Incluir todos los routers

# Administración (incluye platos)
api_router.include_router(admin_router)

# TODO: Descomentar conforme se implementen
# api_router.include_router(auth.router)           # Auth endpoints
# api_router.include_router(restaurants.router)    # Restaurant CRUD
# api_router.include_router(categories.router)     # Category CRUD
# api_router.include_router(menu.router)           # Public menu
# api_router.include_router(qr.router)             # QR generation
api_router.include_router(upload.router)           # Image upload
# api_router.include_router(analytics.router)      # Analytics

