import pytest
from io import BytesIO
from httpx import AsyncClient
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from main import app
from app.api.dependencies import get_current_user, get_db
from app.models.user import User


# Mock del usuario actual para saltar la autenticación real en los tests
def get_mock_user():
    return User(id=uuid4(), email="test@example.com")


@pytest.fixture
async def client(db_session: AsyncSession):
    """Fixture para cliente HTTP de prueba — mismo patrón que test_dish_api."""
    app.dependency_overrides[get_current_user] = get_mock_user

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_upload_invalid_type(client):
    """Prueba que el sistema rechaza archivos que no son imágenes."""
    files = {"file": ("test.txt", b"plain text", "text/plain")}
    response = await client.post("/api/v1/admin/upload/dish", files=files)
    assert response.status_code == 400
    assert "Formato no permitido" in response.json()["detail"]


@pytest.mark.asyncio
async def test_upload_file_too_large(client):
    """Prueba que el sistema rechaza archivos que excedan el límite (5MB)."""
    # 6MB de contenido basura
    large_content = b"0" * (6 * 1024 * 1024)
    files = {"file": ("large.jpg", large_content, "image/jpeg")}
    response = await client.post("/api/v1/admin/upload/dish", files=files)
    assert response.status_code == 400
    assert "demasiado grande" in response.json()["detail"].lower()
