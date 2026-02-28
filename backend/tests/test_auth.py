"""
Tests para los endpoints de autenticación: /api/v1/auth/*
Cubre registro, login, refresh, logout y /me.
"""
import pytest
from httpx import AsyncClient

from app.core.config import settings


API_PREFIX = settings.API_V1_STR


class TestRegister:
    """Tests para POST /api/v1/auth/register"""

    async def test_register_success(self, client: AsyncClient):
        """Registro exitoso retorna JWT."""
        response = await client.post(
            f"{API_PREFIX}/auth/register",
            json={"email": "new@example.com", "password": "securepass123"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_register_duplicate_email(self, client: AsyncClient, test_user):
        """Registro con email duplicado retorna 400."""
        response = await client.post(
            f"{API_PREFIX}/auth/register",
            json={"email": "test@example.com", "password": "anotherpass123"},
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()

    async def test_register_invalid_email(self, client: AsyncClient):
        """Registro con email inválido retorna 422."""
        response = await client.post(
            f"{API_PREFIX}/auth/register",
            json={"email": "not-an-email", "password": "securepass123"},
        )
        assert response.status_code == 422

    async def test_register_short_password(self, client: AsyncClient):
        """Registro con contraseña corta (<8 chars) retorna 422."""
        response = await client.post(
            f"{API_PREFIX}/auth/register",
            json={"email": "short@example.com", "password": "1234567"},
        )
        assert response.status_code == 422

    async def test_register_missing_fields(self, client: AsyncClient):
        """Registro sin campos retorna 422."""
        response = await client.post(f"{API_PREFIX}/auth/register", json={})
        assert response.status_code == 422


class TestLogin:
    """Tests para POST /api/v1/auth/login"""

    async def test_login_success(self, client: AsyncClient, test_user):
        """Login con credenciales correctas retorna JWT."""
        response = await client.post(
            f"{API_PREFIX}/auth/login",
            json={"email": "test@example.com", "password": "testpassword123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient, test_user):
        """Login con contraseña incorrecta retorna 401."""
        response = await client.post(
            f"{API_PREFIX}/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 401
        assert "incorrect" in response.json()["detail"].lower()

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Login con usuario que no existe retorna 401."""
        response = await client.post(
            f"{API_PREFIX}/auth/login",
            json={"email": "nobody@example.com", "password": "somepassword"},
        )
        assert response.status_code == 401

    async def test_login_missing_fields(self, client: AsyncClient):
        """Login sin campos retorna 422."""
        response = await client.post(f"{API_PREFIX}/auth/login", json={})
        assert response.status_code == 422


class TestMe:
    """Tests para GET /api/v1/auth/me"""

    async def test_me_authenticated(self, client: AsyncClient, test_user, auth_headers):
        """GET /me con token válido retorna datos del usuario."""
        response = await client.get(f"{API_PREFIX}/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert "id" in data

    async def test_me_no_token(self, client: AsyncClient):
        """GET /me sin token retorna 403."""
        response = await client.get(f"{API_PREFIX}/auth/me")
        assert response.status_code == 403

    async def test_me_invalid_token(self, client: AsyncClient):
        """GET /me con token inválido retorna 401."""
        response = await client.get(
            f"{API_PREFIX}/auth/me",
            headers={"Authorization": "Bearer invalid-token-here"},
        )
        assert response.status_code == 401


class TestRefresh:
    """Tests para POST /api/v1/auth/refresh"""

    async def test_refresh_success(self, client: AsyncClient, auth_headers):
        """Refresh con token válido retorna nuevo JWT."""
        response = await client.post(
            f"{API_PREFIX}/auth/refresh", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_refresh_no_token(self, client: AsyncClient):
        """Refresh sin token retorna 403."""
        response = await client.post(f"{API_PREFIX}/auth/refresh")
        assert response.status_code == 403


class TestLogout:
    """Tests para POST /api/v1/auth/logout"""

    async def test_logout_success(self, client: AsyncClient, auth_headers):
        """Logout con token válido retorna confirmación."""
        response = await client.post(
            f"{API_PREFIX}/auth/logout", headers=auth_headers
        )
        assert response.status_code == 200
        assert "logged out" in response.json()["message"].lower()

    async def test_logout_no_token(self, client: AsyncClient):
        """Logout sin token retorna 403."""
        response = await client.post(f"{API_PREFIX}/auth/logout")
        assert response.status_code == 403


class TestFullAuthFlow:
    """Test de flujo completo: register → login → me → refresh → logout."""

    async def test_full_flow(self, client: AsyncClient):
        """Flujo completo de autenticación funciona end-to-end."""
        # 1. Register
        resp = await client.post(
            f"{API_PREFIX}/auth/register",
            json={"email": "flow@example.com", "password": "flowpass123"},
        )
        assert resp.status_code == 201
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Me
        resp = await client.get(f"{API_PREFIX}/auth/me", headers=headers)
        assert resp.status_code == 200
        assert resp.json()["email"] == "flow@example.com"

        # 3. Login
        resp = await client.post(
            f"{API_PREFIX}/auth/login",
            json={"email": "flow@example.com", "password": "flowpass123"},
        )
        assert resp.status_code == 200
        new_token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {new_token}"}

        # 4. Refresh
        resp = await client.post(f"{API_PREFIX}/auth/refresh", headers=headers)
        assert resp.status_code == 200
        refreshed_token = resp.json()["access_token"]
        assert refreshed_token  # Token válido recibido

        # 5. Logout (use refreshed token)
        resp = await client.post(
            f"{API_PREFIX}/auth/logout",
            headers={"Authorization": f"Bearer {refreshed_token}"},
        )
        assert resp.status_code == 200
