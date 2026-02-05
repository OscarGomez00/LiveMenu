"""
Repository base para User.
Implementa operaciones CRUD básicas.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from uuid import UUID

from app.models.user import User
from app.schemas.user import UserCreate


class UserRepository:
    """Repositorio para operaciones de base de datos de usuarios."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtener usuario por ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalars().first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalars().first()
    
    async def create(self, user_data: UserCreate, hashed_password: str) -> User:
        """Crear un nuevo usuario con password hasheado."""
        user = User(
            email=user_data.email,
            hashed_password=hashed_password
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        """Eliminar un usuario."""
        user = await self.get_by_id(user_id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
            return True
        return False
