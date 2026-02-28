import pytest
import uuid
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.dish_repository import DishRepository

@pytest.mark.asyncio
async def test_create_dish(db_session: AsyncSession, sample_category):
    """Prueba la creación de un plato."""
    repo = DishRepository(db_session)
    dish_data = {
        "nombre": "Plato Test",
        "descripcion": "Descripción Test",
        "precio": Decimal("10.50"),
        "category_id": sample_category.id,
        "disponible": True,
        "destacado": False,
        "etiquetas": ["test"],
        "posicion": 1
    }
    
    dish = await repo.create(dish_data)
    
    assert dish.id is not None
    assert dish.nombre == "Plato Test"
    assert dish.precio == Decimal("10.50")
    assert dish.category_id == sample_category.id

@pytest.mark.asyncio
async def test_get_dish_by_id(db_session: AsyncSession, sample_category):
    """Prueba la obtención de un plato por ID."""
    repo = DishRepository(db_session)
    dish_data = {
        "nombre": "Get Test",
        "precio": Decimal("5.00"),
        "category_id": sample_category.id
    }
    created_dish = await repo.create(dish_data)
    
    fetched_dish = await repo.get_by_id(created_dish.id)
    
    assert fetched_dish is not None
    assert fetched_dish.id == created_dish.id
    assert fetched_dish.nombre == "Get Test"

@pytest.mark.asyncio
async def test_get_all_dishes(db_session: AsyncSession, sample_category):
    """Prueba el listado de platos con filtros."""
    repo = DishRepository(db_session)
    
    # Crear dos platos
    await repo.create({"nombre": "Dish 1", "precio": Decimal("10"), "category_id": sample_category.id, "disponible": True})
    await repo.create({"nombre": "Dish 2", "precio": Decimal("20"), "category_id": sample_category.id, "disponible": False})
    
    # Listar todos
    dishes, total = await repo.get_all()
    assert total == 2
    
    # Filtrar por disponible
    dishes_available, total_available = await repo.get_all(disponible=True)
    assert total_available == 1
    assert dishes_available[0].nombre == "Dish 1"

@pytest.mark.asyncio
async def test_soft_delete_dish(db_session: AsyncSession, sample_category):
    """Prueba el soft delete de un plato."""
    repo = DishRepository(db_session)
    dish = await repo.create({"nombre": "Delete Me", "precio": Decimal("10"), "category_id": sample_category.id})
    
    # Eliminar
    deleted_dish = await repo.soft_delete(dish.id)
    assert deleted_dish.eliminado_en is not None
    
    # Verificar que no aparece en get_by_id (que filtra por eliminado_en is None)
    fetched_dish = await repo.get_by_id(dish.id)
    assert fetched_dish is None

@pytest.mark.asyncio
async def test_toggle_availability(db_session: AsyncSession, sample_category):
    """Prueba el cambio de disponibilidad."""
    repo = DishRepository(db_session)
    dish = await repo.create({"nombre": "Toggle Test", "precio": Decimal("10"), "category_id": sample_category.id, "disponible": True})
    
    updated_dish = await repo.toggle_availability(dish.id)
    assert updated_dish.disponible is False
    
    updated_dish = await repo.toggle_availability(dish.id)
    assert updated_dish.disponible is True
