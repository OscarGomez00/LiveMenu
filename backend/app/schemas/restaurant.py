from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional, Any


# Schemas de entrada
class RestaurantCreate(BaseModel):
    """Schema para crear un restaurante."""
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    horarios: Optional[Any] = None


class RestaurantUpdate(BaseModel):
    """Schema para actualizar un restaurante."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    logo_url: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    horarios: Optional[Any] = None


# Schemas de salida
class RestaurantResponse(BaseModel):
    """Schema de respuesta con datos de restaurante."""
    id: UUID
    nombre: str
    slug: str
    descripcion: Optional[str] = None
    logo_url: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    horarios: Optional[Any] = None
    owner_id: UUID

    model_config = {"from_attributes": True}
