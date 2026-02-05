from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


# Schemas de entrada
class RestaurantCreate(BaseModel):
    """Schema para crear un restaurante."""
    nombre: str = Field(..., min_length=1, max_length=200)
    slug: str = Field(..., min_length=1, max_length=200, 
                      description="URL-friendly identifier (ej: mi-restaurante)")


class RestaurantUpdate(BaseModel):
    """Schema para actualizar un restaurante."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    slug: Optional[str] = Field(None, min_length=1, max_length=200)


# Schemas de salida
class RestaurantResponse(BaseModel):
    """Schema de respuesta con datos de restaurante."""
    id: UUID
    nombre: str
    slug: str
    owner_id: UUID
    
    model_config = {"from_attributes": True}
