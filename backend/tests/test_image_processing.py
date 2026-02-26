import pytest
from io import BytesIO
from fastapi.testclient import TestClient
from app.api.dependencies import get_current_user
from app.models.user import User
from main import app
import uuid

# Mock del usuario actual para saltar la autenticación real en los tests
async def override_get_current_user():
    return User(
        id=uuid.uuid4(),
        email="test@example.com",
        full_name="Test User"
    )

app.dependency_overrides[get_current_user] = override_get_current_user
client = TestClient(app)

def test_upload_dish_image_success():
    """Prueba la subida exitosa de una imagen de plato."""
    # Crear una imagen falsa en memoria
    file_content = b"fake-image-binary-content"
    files = {"file": ("test.jpg", file_content, "image/jpeg")}
    
    response = client.post("/api/v1/upload/dish", files=files)
    
    assert response.status_code == 200
    assert "url" in response.json()
    assert response.json()["url"].startswith("/uploads/dishes/")

def test_upload_invalid_type():
    """Prueba que el sistema rechaza archivos que no son imágenes."""
    files = {"file": ("test.txt", b"plain text", "text/plain")}
    
    response = client.post("/api/v1/upload/dish", files=files)
    
    assert response.status_code == 400
    assert "Formato no permitido" in response.json()["detail"]

def test_upload_file_too_large():
    """Prueba que el sistema rechaza archivos excedan el límite (2MB)."""
    # 3MB de contenido basura
    large_content = b"0" * (3 * 1024 * 1024)
    files = {"file": ("large.jpg", large_content, "image/jpeg")}
    
    response = client.post("/api/v1/upload/dish", files=files)
    
    assert response.status_code == 400
    assert "Too large" in response.json()["detail"] or "demasiado grande" in response.json()["detail"].lower()
