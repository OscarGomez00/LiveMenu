"""
Endpoints de Autenticación: registro, login, refresh, logout y perfil del usuario.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.api.dependencies import get_current_user
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=201)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Registrar un nuevo usuario.

    - **email**: email válido (único)
    - **password**: mínimo 8 caracteres

    Retorna un token JWT para autenticación inmediata.
    """
    auth_service = AuthService(db)
    return await auth_service.register(user_data)


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """
    Iniciar sesión con email y contraseña.

    Retorna un token JWT válido por el tiempo configurado.
    """
    auth_service = AuthService(db)
    return await auth_service.login(login_data)


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Refrescar el token JWT.

    Requiere un token JWT válido y retorna uno nuevo con expiración renovada.
    """
    auth_service = AuthService(db)
    return auth_service.create_token_for_user(current_user)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Cerrar sesión.

    Con JWT stateless, el logout se maneja del lado del cliente
    eliminando el token. Este endpoint valida el token y confirma
    la operación.
    """
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Obtener información del usuario autenticado.

    Requiere token JWT en header: `Authorization: Bearer <token>`
    """
    return current_user
