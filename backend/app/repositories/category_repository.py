from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category

class CategoryRepository:
    """
    Repositorio para gestionar operaciones de base de datos para Categorías.
    Implementación mínima requerida por el servicio de platos.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, id: UUID) -> Optional[Category]:
        """Obtener una categoría por su ID."""
        result = await self.db.execute(select(Category).where(Category.id == id))
        return result.scalar_one_or_none()
