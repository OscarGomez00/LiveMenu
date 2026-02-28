"""
Service - Lógica de negocio de Autenticación.
Maneja registro, login y generación de tokens.
"""
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash, verify_password, create_access_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, Token


class AuthService:
    """Servicio de autenticación: registro, login, tokens."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)

    async def register(self, user_data: UserCreate) -> Token:
        """
        Registra un nuevo usuario.
        - Verifica que el email no exista.
        - Hashea la contraseña.
        - Crea el usuario en DB.
        - Retorna un token JWT.
        """
        existing_user = await self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        hashed_password = get_password_hash(user_data.password)
        user = await self.user_repo.create(user_data, hashed_password)

        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return Token(access_token=access_token, token_type="bearer")

    async def login(self, login_data: UserLogin) -> Token:
        """
        Autentica un usuario con email y contraseña.
        - Busca usuario por email.
        - Verifica la contraseña.
        - Retorna un token JWT.
        """
        user = await self.user_repo.get_by_email(login_data.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return Token(access_token=access_token, token_type="bearer")

    def create_token_for_user(self, user: User) -> Token:
        """Genera un nuevo token JWT para un usuario existente."""
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=access_token, token_type="bearer")

    async def get_current_user_info(self, user: User) -> dict:
        """Retorna información del usuario autenticado."""
        return {
            "id": str(user.id),
            "email": user.email,
        }
