"""
Endpoints de API para gestión de platos (admin).
Requiere autenticación JWT para todos los endpoints.
"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.dish_service import DishService
from app.schemas.dish import (
    DishCreate,
    DishUpdate,
    DishResponse,
    DishListResponse,
    AvailabilityToggle
)

router = APIRouter(prefix="/dishes", tags=["Platos (Admin)"])


@router.get("", response_model=DishListResponse)
async def list_dishes(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de registros a retornar"),
    category_id: Optional[UUID] = Query(None, description="Filtrar por categoría"),
    disponible: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    destacado: Optional[bool] = Query(None, description="Filtrar por destacado"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Listar platos con filtros opcionales y paginación.
    
    - **skip**: Offset para paginación (default: 0)
    - **limit**: Límite de resultados (default: 100, max: 500)
    - **category_id**: UUID de categoría para filtrar (opcional)
    - **disponible**: true/false para filtrar por disponibilidad (opcional)
    - **destacado**: true/false para filtrar platos destacados (opcional)
    
    Requiere autenticación JWT.
    """
    service = DishService(db)
    return await service.get_dishes(
        skip=skip,
        limit=limit,
        category_id=category_id,
        disponible=disponible,
        destacado=destacado
    )


@router.get("/{id}", response_model=DishResponse)
async def get_dish(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtener un plato por su ID.
    
    - **dish_id**: UUID del plato
    
    Requiere autenticación JWT.
    """
    service = DishService(db)
    return await service.get_dish_by_id(id)


@router.post("", response_model=DishResponse, status_code=201)
async def create_dish(
    dish_data: DishCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crear un nuevo plato.
    
    Campos requeridos:
    - **nombre**: Nombre del plato (máx 100 caracteres)
    - **precio**: Precio del plato (decimal 10,2)
    - **category_id**: UUID de la categoría
    
    Campos opcionales:
    - **descripcion**: Descripción del plato (máx 300 caracteres)
    - **precio_oferta**: Precio de oferta (debe ser menor que precio)
    - **imagen_url**: URL de la imagen
    - **disponible**: Disponibilidad (default: true)
    - **destacado**: Destacado en menú (default: false)
    - **etiquetas**: Array de etiquetas ["vegetariano", "picante", etc.]
    - **posicion**: Posición para ordenamiento
    
    Requiere autenticación JWT.
    """
    service = DishService(db)
    return await service.create_dish(dish_data)


@router.put("/{id}", response_model=DishResponse)
async def update_dish(
    id: UUID,
    dish_data: DishUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Actualizar un plato existente.
    
    Todos los campos son opcionales. Solo se actualizan los campos proporcionados.
    
    - **dish_id**: UUID del plato a actualizar
    
    Requiere autenticación JWT.
    """
    service = DishService(db)
    return await service.update_dish(id, dish_data)


@router.delete("/{id}")
async def delete_dish(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Eliminar un plato (soft delete).
    
    El plato se marca como eliminado pero no se elimina físicamente de la base de datos.
    
    - **dish_id**: UUID del plato a eliminar
    
    Requiere autenticación JWT.
    """
    service = DishService(db)
    return await service.delete_dish(id)


@router.patch("/{id}/availability", response_model=DishResponse)
async def toggle_dish_availability(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Alternar disponibilidad de un plato.
    
    Cambia el estado de disponible (true <-> false).
    
    - **dish_id**: UUID del plato
    
    Requiere autenticación JWT.
    """
    service = DishService(db)
    return await service.toggle_dish_availability(id)
