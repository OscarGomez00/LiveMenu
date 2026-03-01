"""
Service - Lógica de negocio de Restaurant.
Maneja CRUD con validaciones y generación de slug.
"""
import re
import unicodedata
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.restaurant_repository import RestaurantRepository
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantResponse
from app.models.restaurant import Restaurant


def generate_slug(name: str) -> str:
    """Genera un slug URL-friendly a partir de un nombre (sin acentos)."""
    # Normalizar unicode y eliminar acentos
    normalized = unicodedata.normalize("NFKD", name)
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii")
    return re.sub(r'[^a-z0-9]+', '-', ascii_name.lower()).strip('-')


class RestaurantService:
    """Servicio para gestionar lógica de negocio de restaurantes."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = RestaurantRepository(db)

    async def get_by_owner(self, owner_id: UUID) -> Restaurant:
        """Obtener el restaurante del usuario (primero encontrado)."""
        restaurants = await self.repo.get_by_owner(owner_id)
        if not restaurants:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No tienes un restaurante registrado",
            )
        return restaurants[0]

    async def create(self, data: RestaurantCreate, owner_id: UUID) -> Restaurant:
        """Crear un restaurante con slug generado automáticamente."""
        # Verificar que el usuario no tenga ya un restaurante
        existing = await self.repo.get_by_owner(owner_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya tienes un restaurante registrado",
            )

        slug = generate_slug(data.nombre)

        # Verificar slug único
        existing_slug = await self.repo.get_by_slug(slug)
        if existing_slug:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre genera un slug que ya está en uso",
            )

        restaurant = Restaurant(
            nombre=data.nombre,
            slug=slug,
            descripcion=data.descripcion,
            logo_url=data.logo_url,
            telefono=data.telefono,
            direccion=data.direccion,
            horarios=data.horarios,
            owner_id=owner_id,
        )
        self.db.add(restaurant)
        await self.db.commit()
        await self.db.refresh(restaurant)
        return restaurant

    async def update(self, data: RestaurantUpdate, owner_id: UUID) -> Restaurant:
        """Actualizar el restaurante del usuario."""
        restaurant = await self.get_by_owner(owner_id)

        update_data = data.model_dump(exclude_unset=True)

        # Si cambia el nombre, regenerar slug
        if "nombre" in update_data and update_data["nombre"]:
            new_slug = generate_slug(update_data["nombre"])
            if new_slug != restaurant.slug:
                existing_slug = await self.repo.get_by_slug(new_slug)
                if existing_slug and existing_slug.id != restaurant.id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="El nombre genera un slug que ya está en uso",
                    )
                update_data["slug"] = new_slug

        for key, value in update_data.items():
            if hasattr(restaurant, key):
                setattr(restaurant, key, value)

        await self.db.commit()
        await self.db.refresh(restaurant)
        return restaurant

    async def delete(self, owner_id: UUID) -> dict:
        """Eliminar el restaurante del usuario."""
        restaurant = await self.get_by_owner(owner_id)
        await self.repo.delete(restaurant)
        return {"message": "Restaurante eliminado exitosamente"}
