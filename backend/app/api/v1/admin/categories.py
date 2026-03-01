"""
Endpoints de API para gestión de categorías (admin).
Requiere autenticación JWT para todos los endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.category_service import CategoryService
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryReorder,
)

router = APIRouter(prefix="/categories", tags=["Categorías (Admin)"])


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Listar categorías del restaurante ordenadas por posición."""
    service = CategoryService(db)
    return await service.get_all(current_user.id)


@router.post("", response_model=CategoryResponse, status_code=201)
async def create_category(
    data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Crear una nueva categoría."""
    service = CategoryService(db)
    return await service.create(data, current_user.id)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actualizar una categoría existente."""
    service = CategoryService(db)
    return await service.update(category_id, data, current_user.id)


@router.delete("/{category_id}")
async def delete_category(
    category_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Eliminar una categoría (solo si no tiene platos asociados)."""
    service = CategoryService(db)
    return await service.delete(category_id, current_user.id)


@router.patch("/reorder", response_model=List[CategoryResponse])
async def reorder_categories(
    data: CategoryReorder,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Reordenar categorías."""
    service = CategoryService(db)
    return await service.reorder(data, current_user.id)
