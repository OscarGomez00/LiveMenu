from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from typing import Optional


# Schemas de entrada
class UserCreate(BaseModel):
    """Schema para registrar un nuevo usuario."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)


class UserLogin(BaseModel):
    """Schema para login de usuario."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema para actualizar datos de usuario."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


# Schemas de salida
class UserResponse(BaseModel):
    """Schema de respuesta con datos de usuario (sin password)."""
    id: UUID
    email: EmailStr
    
    model_config = {"from_attributes": True}


# Schemas de autenticación
class Token(BaseModel):
    """Schema para respuesta de token JWT."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema para datos decodificados del token."""
    user_id: Optional[UUID] = None
