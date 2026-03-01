"""
Repositorio para operaciones de base de datos de Category.
Implementa el patrón Repository para acceso a datos.
"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


class CategoryRepository:
    """Repositorio para gestionar operaciones CRUD de categorías."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: UUID) -> Optional[Category]:
        """Obtener una categoría por su ID."""
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_all_by_restaurant(self, restaurant_id: UUID) -> List[Category]:
        """Obtener todas las categorías de un restaurante ordenadas por posición."""
        result = await self.db.execute(
            select(Category)
            .where(Category.restaurant_id == restaurant_id)
            .order_by(Category.posicion.asc(), Category.nombre.asc())
        )
        return list(result.scalars().all())

    async def create(self, data: dict) -> Category:
        """Crear una nueva categoría."""
        if data.get("posicion") is None:
            max_pos_query = select(func.max(Category.posicion)).where(
                Category.restaurant_id == data["restaurant_id"]
            )
            result = await self.db.execute(max_pos_query)
            max_pos = result.scalar()
            data["posicion"] = (max_pos or 0) + 1

        category = Category(**data)
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def update(self, category_id: UUID, data: dict) -> Optional[Category]:
        """Actualizar una categoría existente."""
        category = await self.get_by_id(category_id)
        if not category:
            return None

        for key, value in data.items():
            if hasattr(category, key):
                setattr(category, key, value)

        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete(self, category_id: UUID) -> bool:
        """Eliminar una categoría (solo si no tiene platos)."""
        category = await self.get_by_id(category_id)
        if not category:
            return False

        await self.db.delete(category)
        await self.db.commit()
        return True

    async def has_dishes(self, category_id: UUID) -> bool:
        """Verificar si una categoría tiene platos activos asociados."""
        from app.models.dish import Dish
        result = await self.db.execute(
            select(func.count(Dish.id)).where(
                and_(
                    Dish.category_id == category_id,
                    Dish.eliminado_en.is_(None),
                )
            )
        )
        count = result.scalar()
        return count > 0

    async def reorder(self, restaurant_id: UUID, ordered_ids: List[UUID]) -> List[Category]:
        """Reordenar categorías según la lista de IDs proporcionada."""
        categories = await self.get_all_by_restaurant(restaurant_id)
        cat_map = {cat.id: cat for cat in categories}

        for i, cat_id in enumerate(ordered_ids):
            if cat_id in cat_map:
                cat_map[cat_id].posicion = i

        await self.db.commit()
        return await self.get_all_by_restaurant(restaurant_id)
