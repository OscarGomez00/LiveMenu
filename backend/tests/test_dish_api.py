import pytest
from httpx import AsyncClient
from uuid import uuid4
from decimal import Decimal
from main import app
from app.api.dependencies import get_current_user, get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

# Mock de usuario para saltar autenticación JWT real en tests
def get_mock_user():
    return User(id=uuid4(), email="test@example.com")

@pytest.fixture
async def client(db_session: AsyncSession):
    """Fixture para cliente HTTP de prueba."""
    # Override de usuario actual
    app.dependency_overrides[get_current_user] = get_mock_user
    
    # Override de base de datos para usar SQLite de test
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_api_list_dishes(client, sample_category):
    """Prueba el endpoint GET /api/v1/admin/dishes."""
    response = await client.get("/api/v1/admin/dishes")
    assert response.status_code == 200
    data = response.json()
    assert "dishes" in data
    assert "total" in data

@pytest.mark.asyncio
async def test_api_create_dish(client, sample_category):
    """Prueba el endpoint POST /api/v1/admin/dishes."""
    dish_data = {
        "nombre": "API Dish",
        "precio": 10.99,
        "category_id": str(sample_category.id)
    }
    response = await client.post("/api/v1/admin/dishes", json=dish_data)
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "API Dish"
    assert data["precio"] == "10.99"

@pytest.mark.asyncio
async def test_api_get_dish_not_found(client):
    """Prueba el error 404 al buscar plato inexistente."""
    response = await client.get(f"/api/v1/admin/dishes/{uuid4()}")
    assert response.status_code == 404
