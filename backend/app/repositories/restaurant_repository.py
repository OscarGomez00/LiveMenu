"""
Repository - Acceso a datos de Restaurant.
Operaciones CRUD para la tabla restaurants.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID

from app.models.restaurant import Restaurant


class RestaurantRepository:
    """Repositorio para operaciones de base de datos de restaurantes."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, restaurant_id: UUID) -> Optional[Restaurant]:
        """Obtener restaurante por ID."""
        result = await self.db.execute(
            select(Restaurant).where(Restaurant.id == restaurant_id)
        )
        return result.scalars().first()

    async def get_by_slug(self, slug: str) -> Optional[Restaurant]:
        """Obtener restaurante por slug."""
        result = await self.db.execute(
            select(Restaurant).where(Restaurant.slug == slug)
        )
        return result.scalars().first()

    async def get_by_owner(self, owner_id: UUID) -> list[Restaurant]:
        """Obtener todos los restaurantes de un usuario."""
        result = await self.db.execute(
            select(Restaurant).where(Restaurant.owner_id == owner_id)
        )
        return list(result.scalars().all())

    async def create(self, nombre: str, slug: str, owner_id: UUID) -> Restaurant:
        """Crear un nuevo restaurante."""
        restaurant = Restaurant(
            nombre=nombre,
            slug=slug,
            owner_id=owner_id,
        )
        self.db.add(restaurant)
        await self.db.commit()
        await self.db.refresh(restaurant)
        return restaurant

    async def update(self, restaurant: Restaurant, **kwargs) -> Restaurant:
        """Actualizar un restaurante existente."""
        for key, value in kwargs.items():
            if value is not None and hasattr(restaurant, key):
                setattr(restaurant, key, value)
        await self.db.commit()
        await self.db.refresh(restaurant)
        return restaurant

    async def delete(self, restaurant: Restaurant) -> bool:
        """Eliminar un restaurante."""
        await self.db.delete(restaurant)
        await self.db.commit()
        return True
