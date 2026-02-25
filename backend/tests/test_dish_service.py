import pytest
from uuid import uuid4
from decimal import Decimal
from fastapi import HTTPException
from app.services.dish_service import DishService
from app.schemas.dish import DishCreate, DishUpdate

@pytest.mark.asyncio
async def test_create_dish_service(db_session, sample_category):
    """Prueba la creación de un plato a través del servicio."""
    service = DishService(db_session)
    dish_in = DishCreate(
        nombre="Service Dish",
        precio=Decimal("15.00"),
        category_id=sample_category.id
    )
    
    dish = await service.create_dish(dish_in)
    
    assert dish.id is not None
    assert dish.nombre == "Service Dish"
    assert dish.precio == Decimal("15.00")

@pytest.mark.asyncio
async def test_create_dish_invalid_category(db_session):
    """Prueba que falla al crear un plato con categoría inexistente."""
    service = DishService(db_session)
    dish_in = DishCreate(
        nombre="Fail Dish",
        precio=Decimal("10.00"),
        category_id=uuid4() # ID aleatorio
    )
    
    with pytest.raises(HTTPException) as excinfo:
        await service.create_dish(dish_in)
    
    assert excinfo.value.status_code == 404
    assert "Categoría" in excinfo.value.detail

@pytest.mark.asyncio
async def test_create_dish_invalid_price_offer(db_session, sample_category):
    """Prueba que el precio de oferta no sea mayor al precio normal."""
    service = DishService(db_session)
    # Pydantic validará esto en el schema, pero el servicio también tiene una capa de validación
    # En este caso, DishCreate tiene un field_validator, así que testaremos la validación de Pydantic
    # o la del servicio si pasamos datos que burlen a Pydantic (usando dict directamente)
    
    from pydantic import ValidationError
    
    with pytest.raises(ValidationError):
        dish_in = DishCreate(
            nombre="Offer Dish",
            precio=Decimal("10.00"),
            precio_oferta=Decimal("15.00"), # Mayor que precio
            category_id=sample_category.id
        )
    
    # Pydantic levantará ValidationError antes de llegar al servicio
    # Pero vamos a testear la lógica de DishService.create_dish que tiene un check manual
    
    dish_data = {
        "nombre": "Offer Dish",
        "precio": Decimal("10.00"),
        "precio_oferta": Decimal("15.00"),
        "category_id": sample_category.id
    }
    
    # Usamos mock para saltar validación de Pydantic si es necesario, 
    # o simplemente confiamos en que Pydantic hace su trabajo.
    # Aquí testearemos el HTTPException que lanza el servicio
    
    from types import SimpleNamespace
    mock_dish_in = SimpleNamespace(
        precio=Decimal("10.00"),
        precio_oferta=Decimal("15.00"),
        category_id=sample_category.id,
        model_dump=lambda: dish_data
    )
    
    with pytest.raises(HTTPException) as excinfo:
        await service.create_dish(mock_dish_in)
    
    assert excinfo.value.status_code == 400
    assert "precio de oferta" in excinfo.value.detail

@pytest.mark.asyncio
async def test_update_dish_service(db_session, sample_category):
    """Prueba la actualización de un plato."""
    service = DishService(db_session)
    dish_in = DishCreate(nombre="Original", precio=Decimal("10"), category_id=sample_category.id)
    dish = await service.create_dish(dish_in)
    
    update_in = DishUpdate(nombre="Updated")
    updated_dish = await service.update_dish(dish.id, update_in)
    
    assert updated_dish.nombre == "Updated"
    assert updated_dish.precio == Decimal("10") # Mantiene el original

@pytest.mark.asyncio
async def test_delete_dish_service(db_session, sample_category):
    """Prueba la eliminación a través del servicio."""
    service = DishService(db_session)
    dish_in = DishCreate(nombre="To Delete", precio=Decimal("10"), category_id=sample_category.id)
    dish = await service.create_dish(dish_in)
    
    response = await service.delete_dish(dish.id)
    assert "exitosamente" in response["message"]
    
    with pytest.raises(HTTPException):
        await service.get_dish_by_id(dish.id)
