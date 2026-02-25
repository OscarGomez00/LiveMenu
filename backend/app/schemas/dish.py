from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


# Schemas de entrada
class DishCreate(BaseModel):
    """Schema para crear un plato."""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del plato")
    descripcion: Optional[str] = Field(None, max_length=300, description="Descripción del plato")
    precio: Decimal = Field(..., ge=0, description="Precio del plato (ej: 12.50)")
    precio_oferta: Optional[Decimal] = Field(None, ge=0, description="Precio de oferta (opcional)")
    category_id: UUID = Field(..., description="ID de la categoría")
    imagen_url: Optional[str] = Field(None, description="URL de la imagen")
    disponible: bool = Field(default=True, description="Indica si el plato está disponible")
    destacado: bool = Field(default=False, description="Indica si el plato es destacado")
    etiquetas: Optional[List[str]] = Field(None, description="Etiquetas como 'vegetariano', 'picante', etc.")
    posicion: Optional[int] = Field(None, ge=0, description="Posición para ordenamiento")
    
    @field_validator('precio_oferta')
    @classmethod
    def validate_precio_oferta(cls, v, info):
        """Validar que precio_oferta sea menor que precio."""
        if v is not None and 'precio' in info.data:
            precio = info.data['precio']
            if v > precio:
                raise ValueError('El precio de oferta debe ser menor o igual al precio normal')
        return v


class DishUpdate(BaseModel):
    """Schema para actualizar un plato."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=300)
    precio: Optional[Decimal] = Field(None, ge=0)
    precio_oferta: Optional[Decimal] = Field(None, ge=0)
    category_id: Optional[UUID] = None
    imagen_url: Optional[str] = None
    disponible: Optional[bool] = None
    destacado: Optional[bool] = None
    etiquetas: Optional[List[str]] = None
    posicion: Optional[int] = Field(None, ge=0)
    
    @field_validator('precio_oferta')
    @classmethod
    def validate_precio_oferta(cls, v, info):
        """Validar que precio_oferta sea menor que precio si ambos están presentes."""
        if v is not None and 'precio' in info.data and info.data['precio'] is not None:
            if v > info.data['precio']:
                raise ValueError('El precio de oferta debe ser menor o igual al precio normal')
        return v


class AvailabilityToggle(BaseModel):
    """Schema para respuesta de toggle de disponibilidad."""
    disponible: bool


# Schemas de salida
class DishResponse(BaseModel):
    """Schema de respuesta con datos completos de plato."""
    id: UUID
    nombre: str
    descripcion: Optional[str]
    precio: Decimal
    precio_oferta: Optional[Decimal]
    category_id: UUID
    imagen_url: Optional[str]
    disponible: bool
    destacado: bool
    etiquetas: Optional[List[str]]
    posicion: Optional[int]
    creado_en: datetime
    actualizado_en: datetime
    eliminado_en: Optional[datetime]
    
    model_config = {"from_attributes": True}


class DishListResponse(BaseModel):
    """Schema para respuesta paginada de lista de platos."""
    total: int
    skip: int
    limit: int
    dishes: List[DishResponse]

