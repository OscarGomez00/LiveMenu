from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional


# Schemas de entrada
class CategoryCreate(BaseModel):
    """Schema para crear una categoría."""
    nombre: str = Field(..., min_length=1, max_length=200)
    restaurant_id: UUID


class CategoryUpdate(BaseModel):
    """Schema para actualizar una categoría."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)


# Schemas de salida
class CategoryResponse(BaseModel):
    """Schema de respuesta con datos de categoría."""
    id: UUID
    nombre: str
    restaurant_id: UUID
    
    model_config = {"from_attributes": True}
