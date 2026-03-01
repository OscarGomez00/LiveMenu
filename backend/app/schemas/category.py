from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class CategoryCreate(BaseModel):
    """Schema para crear una categoría."""
    nombre: str = Field(..., min_length=1, max_length=50, description="Nombre de la categoría")
    descripcion: Optional[str] = Field(None, max_length=200)
    posicion: Optional[int] = Field(None, ge=0, description="Posición para ordenamiento")
    activa: bool = Field(True, description="Si la categoría está activa")


class CategoryUpdate(BaseModel):
    """Schema para actualizar una categoría."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=200)
    posicion: Optional[int] = Field(None, ge=0)
    activa: Optional[bool] = None


class CategoryResponse(BaseModel):
    """Schema de respuesta de categoría."""
    id: UUID
    nombre: str
    descripcion: Optional[str] = None
    posicion: int = 0
    activa: bool = True
    restaurant_id: UUID
    creado_en: datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


class CategoryReorder(BaseModel):
    """Schema para reordenar categorías."""
    ordered_ids: List[UUID] = Field(..., description="Lista de IDs en el nuevo orden")