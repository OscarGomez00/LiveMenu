from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
from decimal import Decimal


# Schemas de entrada
class DishCreate(BaseModel):
    """Schema para crear un plato."""
    nombre: str = Field(..., min_length=1, max_length=200)
    precio: Decimal = Field(..., ge=0, decimal_places=2, 
                           description="Precio del plato (ej: 12.50)")
    category_id: UUID


class DishUpdate(BaseModel):
    """Schema para actualizar un plato."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    precio: Optional[Decimal] = Field(None, ge=0, decimal_places=2)
    category_id: Optional[UUID] = None


# Schemas de salida
class DishResponse(BaseModel):
    """Schema de respuesta con datos de plato."""
    id: UUID
    nombre: str
    precio: Decimal
    category_id: UUID
    
    model_config = {"from_attributes": True}
