import re
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.session import get_db # Ajusta según tu archivo de BD
from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate, RestaurantResponse

router = APIRouter(
    prefix="/api/v1/admin/restaurant",
    tags=["Admin Restaurante"]
)

# Función auxiliar para el Slug (Regla: generado desde Nombre)
def generate_slug(name: str) -> str:
    return re.sub(r'\W+', '-', name.lower()).strip('-')

@router.get("/", response_model=RestaurantResponse)
async def get_my_restaurant(db: AsyncSession = Depends(get_db)):
    """Obtener restaurante del usuario autenticado (CU-02 paso 2)"""
    # Aquí asumo que filtrarás por el ID del usuario autenticado más adelante
    result = await db.execute(select(Restaurant))
    restaurant = result.scalars().first()
    if not restaurant:
        raise HTTPException(status_code=404, detail="No tienes un restaurante registrado")
    return restaurant

@router.post("/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
async def create_restaurant(data: RestaurantCreate, db: AsyncSession = Depends(get_db)):
    """Crear perfil del restaurante (CU-02 paso 3 y 4)"""
    new_slug = generate_slug(data.nombre)
    
    # Validar que el slug sea único
    existing = await db.execute(select(Restaurant).where(Restaurant.slug == new_slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="El nombre del restaurante ya está en uso")

    db_restaurant = Restaurant(**data.dict(), slug=new_slug)
    db.add(db_restaurant)
    await db.commit()
    await db.refresh(db_restaurant)
    return db_restaurant

@router.put("/", response_model=RestaurantResponse)
async def update_restaurant(data: RestaurantUpdate, db: AsyncSession = Depends(get_db)):
    """Actualizar datos del restaurante (CU-02 paso 4)"""
    # En un caso real, buscarías por el ID del dueño
    result = await db.execute(select(Restaurant))
    db_restaurant = result.scalars().first()
    
    if not db_restaurant:
        raise HTTPException(status_code=404, detail="Restaurante no encontrado")

    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_restaurant, key, value)
        if key == "nombre": # Si cambia el nombre, se actualiza el slug
            db_restaurant.slug = generate_slug(value)

    await db.commit()
    await db.refresh(db_restaurant)
    return db_restaurant