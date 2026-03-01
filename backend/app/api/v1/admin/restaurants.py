"""
Endpoints de API para gestión de restaurante (admin).
Requiere autenticación JWT para todos los endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.restaurant_service import RestaurantService
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantResponse,
)

router = APIRouter(prefix="/restaurant", tags=["Restaurante (Admin)"])


@router.get("", response_model=RestaurantResponse)
async def get_my_restaurant(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Obtener restaurante del usuario autenticado."""
    service = RestaurantService(db)
    return await service.get_by_owner(current_user.id)


@router.post("", response_model=RestaurantResponse, status_code=201)
async def create_restaurant(
    data: RestaurantCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Crear perfil del restaurante."""
    service = RestaurantService(db)
    return await service.create(data, current_user.id)


@router.put("", response_model=RestaurantResponse)
async def update_restaurant(
    data: RestaurantUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualizar datos del restaurante."""
    service = RestaurantService(db)
    return await service.update(data, current_user.id)


@router.delete("")
async def delete_restaurant(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Eliminar el restaurante."""
    service = RestaurantService(db)
    return await service.delete(current_user.id)
