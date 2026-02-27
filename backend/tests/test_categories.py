import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.mark.asyncio
async def test_category_constraints():
    transport = ASGITransport(app=app)
    # Ajusta la ruta según tu Router Principal
    url = "/api/v1/admin/categories/" 

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Validar Máximo 50 caracteres (Regla Técnica CU-03)
        bad_payload = {"nombre": "C" * 51, "posicion": 1}
        response = await ac.post(url, json=bad_payload)
        assert response.status_code == 422
        
        # Validar Creación Exitosa
        good_payload = {
            "nombre": "Bebidas", 
            "descripcion": "Refrescos y jugos",
            "posicion": 1
        }
        # Nota: Aquí fallará hasta que implementes el endpoint real
        # response = await ac.post(url, json=good_payload)
        # assert response.status_code == 201