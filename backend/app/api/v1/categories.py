from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["Admin Categorías"])

@router.get("/", response_model=List[CategoryResponse])
async def list_categories():
    """Lista categorías existentes ordenadas por posición (Requisito 2)"""
    # Aquí irá la lógica de consulta a DB: .order_by(Category.posicion)
    return []

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate):
    """Crea nueva categoría (Requisito 3.1)"""
    return {}

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: str, category: CategoryCreate):
    """Edita categoría existente (Requisito 3.2)"""
    return {}

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str):
    """Elimina categoría (solo si no tiene platos asociados) (Requisito 3.3)"""
    # Aquí validaremos la restricción de platos asociados
    return None