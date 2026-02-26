"""
Router de administración para API v1.
Agrupa todos los endpoints protegidos para gestión del restaurante.
"""
from fastapi import APIRouter
from app.api.v1.admin import dishes

admin_router = APIRouter(prefix="/admin")

# Incluir todos los routers de administración
admin_router.include_router(dishes.router)
# admin_router.include_router(categories.router)
# admin_router.include_router(restaurants.router)
