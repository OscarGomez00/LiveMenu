"""
Tests para CU-03: Gestión de Categorías.
Usa fixtures de conftest: client, auth_headers, test_user, test_restaurant, db_session.
"""
import pytest


@pytest.mark.asyncio
async def test_create_category(client, auth_headers, test_restaurant):
    """Crear categoría exitosamente."""
    payload = {"nombre": "Bebidas", "descripcion": "Refrescos y jugos"}
    response = await client.post(
        "/api/v1/admin/categories", json=payload, headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Bebidas"
    assert data["descripcion"] == "Refrescos y jugos"
    assert data["activa"] is True
    assert data["posicion"] >= 1  # primera categoría


@pytest.mark.asyncio
async def test_create_category_name_too_long(client, auth_headers, test_restaurant):
    """Validación: nombre máximo 50 caracteres."""
    payload = {"nombre": "C" * 51}
    response = await client.post(
        "/api/v1/admin/categories", json=payload, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_category_missing_name(client, auth_headers, test_restaurant):
    """Validación: nombre es obligatorio."""
    payload = {"descripcion": "Sin nombre"}
    response = await client.post(
        "/api/v1/admin/categories", json=payload, headers=auth_headers
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_categories(client, auth_headers, test_restaurant):
    """Listar categorías del restaurante."""
    # Crear dos categorías
    await client.post(
        "/api/v1/admin/categories",
        json={"nombre": "Entradas"},
        headers=auth_headers,
    )
    await client.post(
        "/api/v1/admin/categories",
        json={"nombre": "Postres"},
        headers=auth_headers,
    )

    response = await client.get(
        "/api/v1/admin/categories", headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["nombre"] == "Entradas"
    assert data[1]["nombre"] == "Postres"


@pytest.mark.asyncio
async def test_update_category(client, auth_headers, test_restaurant):
    """Actualizar categoría existente."""
    # Crear
    create_res = await client.post(
        "/api/v1/admin/categories",
        json={"nombre": "Bebidas"},
        headers=auth_headers,
    )
    cat_id = create_res.json()["id"]

    # Actualizar
    response = await client.put(
        f"/api/v1/admin/categories/{cat_id}",
        json={"nombre": "Bebidas Frías", "activa": False},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Bebidas Frías"
    assert data["activa"] is False


@pytest.mark.asyncio
async def test_delete_category(client, auth_headers, test_restaurant):
    """Eliminar categoría sin platos asociados."""
    create_res = await client.post(
        "/api/v1/admin/categories",
        json={"nombre": "Temporal"},
        headers=auth_headers,
    )
    cat_id = create_res.json()["id"]

    response = await client.delete(
        f"/api/v1/admin/categories/{cat_id}", headers=auth_headers
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_unauthenticated_categories(client):
    """Acceso sin token retorna 401/403."""
    response = await client.get("/api/v1/admin/categories")
    assert response.status_code in (401, 403)