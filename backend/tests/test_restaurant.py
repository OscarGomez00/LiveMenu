"""
Tests para CU-02: Gestión de Restaurante.
Usa fixtures de conftest: client, auth_headers, test_user, db_session.
"""
import pytest


@pytest.mark.asyncio
async def test_create_restaurant(client, auth_headers):
    """Crear restaurante exitosamente."""
    payload = {
        "nombre": "Pizzería Tradicional",
        "descripcion": "Auténtica pizza italiana",
        "telefono": "555123456",
        "direccion": "Av. Principal 123",
    }
    response = await client.post(
        "/api/v1/admin/restaurant", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Pizzería Tradicional"
    assert data["slug"] == "pizzeria-tradicional"
    assert data["descripcion"] == "Auténtica pizza italiana"
    assert data["telefono"] == "555123456"


@pytest.mark.asyncio
async def test_create_restaurant_name_too_long(client, auth_headers):
    """Validación: nombre máximo 100 caracteres."""
    payload = {"nombre": "N" * 101}
    response = await client.post(
        "/api/v1/admin/restaurant", json=payload, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_restaurant_missing_name(client, auth_headers):
    """Validación: nombre es obligatorio."""
    payload = {"descripcion": "Sin nombre"}
    response = await client.post(
        "/api/v1/admin/restaurant", json=payload, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_restaurant(client, auth_headers, test_restaurant):
    """Obtener restaurante del usuario autenticado."""
    response = await client.get(
        "/api/v1/admin/restaurant", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == test_restaurant.nombre
    assert data["slug"] == test_restaurant.slug


@pytest.mark.asyncio
async def test_get_restaurant_not_found(client, auth_headers):
    """404 cuando el usuario no tiene restaurante."""
    response = await client.get(
        "/api/v1/admin/restaurant", headers=auth_headers
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_restaurant(client, auth_headers, test_restaurant):
    """Actualizar datos del restaurante."""
    payload = {"nombre": "Nuevo Nombre", "telefono": "999888777"}
    response = await client.put(
        "/api/v1/admin/restaurant", json=payload, headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Nuevo Nombre"
    assert data["telefono"] == "999888777"
    assert data["slug"] == "nuevo-nombre"


@pytest.mark.asyncio
async def test_unauthenticated_access(client):
    """Acceso sin token retorna 401/403."""
    response = await client.get("/api/v1/admin/restaurant")
    assert response.status_code in (401, 403)

