"""
Service - Lógica de negocio de Category.
Maneja CRUD de categorías con validaciones.
"""
from typing import List
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.category_repository import CategoryRepository
from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryReorder
from app.models.category import Category


class CategoryService:
    """Servicio para gestionar lógica de negocio de categorías."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CategoryRepository(db)
        self.restaurant_repo = RestaurantRepository(db)

    async def _get_restaurant_id(self, owner_id: UUID) -> UUID:
        """Obtener el restaurant_id del usuario autenticado."""
        restaurants = await self.restaurant_repo.get_by_owner(owner_id)
        if not restaurants:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tienes un restaurante registrado. Crea uno primero.",
            )
        return restaurants[0].id

    async def get_all(self, owner_id: UUID) -> List[Category]:
        """Obtener todas las categorías del restaurante del usuario."""
        restaurant_id = await self._get_restaurant_id(owner_id)
        return await self.repo.get_all_by_restaurant(restaurant_id)

    async def get_by_id(self, category_id: UUID, owner_id: UUID) -> Category:
        """Obtener una categoría por ID, validando que pertenezca al usuario."""
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Categoría con ID {category_id} no encontrada",
            )
        restaurant_id = await self._get_restaurant_id(owner_id)
        if category.restaurant_id != restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos sobre esta categoría",
            )
        return category

    async def create(self, data: CategoryCreate, owner_id: UUID) -> Category:
        """Crear una nueva categoría."""
        restaurant_id = await self._get_restaurant_id(owner_id)
        cat_data = data.model_dump()
        cat_data["restaurant_id"] = restaurant_id
        return await self.repo.create(cat_data)

    async def update(self, category_id: UUID, data: CategoryUpdate, owner_id: UUID) -> Category:
        """Actualizar una categoría existente."""
        await self.get_by_id(category_id, owner_id)  # Validar pertenencia
        update_data = data.model_dump(exclude_unset=True)
        category = await self.repo.update(category_id, update_data)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada",
            )
        return category

    async def delete(self, category_id: UUID, owner_id: UUID) -> dict:
        """Eliminar una categoría (solo si no tiene platos)."""
        await self.get_by_id(category_id, owner_id)  # Validar pertenencia

        if await self.repo.has_dishes(category_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se puede eliminar: la categoría tiene platos asociados",
            )

        await self.repo.delete(category_id)
        return {"message": "Categoría eliminada exitosamente"}

    async def reorder(self, data: CategoryReorder, owner_id: UUID) -> List[Category]:
        """Reordenar categorías."""
        restaurant_id = await self._get_restaurant_id(owner_id)
        return await self.repo.reorder(restaurant_id, data.ordered_ids)
