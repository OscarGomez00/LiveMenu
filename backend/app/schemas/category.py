from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class CategoryBase(BaseModel):
    nombre: str = Field(..., max_length=50, description="Nombre de la categoría")
    descripcion: Optional[str] = None
    posicion: int = Field(0, description="Usado para ordenamiento")
    activa: bool = True

class CategoryCreate(CategoryBase):
    pass  # Restaurante_ID se suele obtener del contexto del usuario/restaurante

class CategoryResponse(CategoryBase):
    id: UUID
    restaurante_id: UUID
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        from_attributes = True