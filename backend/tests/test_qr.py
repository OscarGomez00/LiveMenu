"""
Tests para los endpoints de generación de QR: /api/v1/admin/qr
Cubre generación PNG/SVG, tamaños, colores y casos de error.
"""
import pytest
from httpx import AsyncClient

from app.core.config import settings


API_PREFIX = settings.API_V1_STR


class TestQRGeneration:
    """Tests para GET /api/v1/admin/qr"""

    async def test_qr_default_png(
        self, client: AsyncClient, auth_headers, test_restaurant
    ):
        """QR sin params retorna PNG tamaño M."""
        response = await client.get(
            f"{API_PREFIX}/admin/qr", headers=auth_headers
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"
        assert "qr-test-restaurant.png" in response.headers.get(
            "content-disposition", ""
        )
        # Verificar que el contenido es un PNG válido (magic bytes)
        assert response.content[:8] == b"\x89PNG\r\n\x1a\n"

    async def test_qr_svg_format(
        self, client: AsyncClient, auth_headers, test_restaurant
    ):
        """QR con format=svg retorna SVG."""
        response = await client.get(
            f"{API_PREFIX}/admin/qr",
            params={"format": "svg"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/svg+xml"
        assert "qr-test-restaurant.svg" in response.headers.get(
            "content-disposition", ""
        )
        # Verificar que el contenido contiene XML/SVG
        content = response.content.decode("utf-8")
        assert "<svg" in content.lower() or "<?xml" in content.lower()

    async def test_qr_size_s(
        self, client: AsyncClient, auth_headers, test_restaurant
    ):
        """QR con size=s retorna PNG."""
        response = await client.get(
            f"{API_PREFIX}/admin/qr",
            params={"size": "s"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    async def test_qr_size_xl(
        self, client: AsyncClient, auth_headers, test_restaurant
    ):
        """QR con size=xl retorna PNG más grande."""
        response = await client.get(
            f"{API_PREFIX}/admin/qr",
            params={"size": "xl"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    async def test_qr_custom_colors(
        self, client: AsyncClient, auth_headers, test_restaurant
    ):
        """QR con colores personalizados funciona."""
        response = await client.get(
            f"{API_PREFIX}/admin/qr",
            params={"color": "FF0000", "bg_color": "00FF00"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    async def test_qr_all_sizes(
        self, client: AsyncClient, auth_headers, test_restaurant
    ):
        """QR funciona con todos los tamaños disponibles."""
        for size in ["s", "m", "l", "xl"]:
            response = await client.get(
                f"{API_PREFIX}/admin/qr",
                params={"size": size},
                headers=auth_headers,
            )
            assert response.status_code == 200, f"Failed for size={size}"

    async def test_qr_invalid_size(
        self, client: AsyncClient, auth_headers, test_restaurant
    ):
        """QR con tamaño inválido retorna 422."""
        response = await client.get(
            f"{API_PREFIX}/admin/qr",
            params={"size": "xxl"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    async def test_qr_invalid_format(
        self, client: AsyncClient, auth_headers, test_restaurant
    ):
        """QR con formato inválido retorna 422."""
        response = await client.get(
            f"{API_PREFIX}/admin/qr",
            params={"format": "gif"},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestQRAuth:
    """Tests de autenticación para el endpoint QR."""

    async def test_qr_no_auth(self, client: AsyncClient):
        """QR sin autenticación retorna 403."""
        response = await client.get(f"{API_PREFIX}/admin/qr")
        assert response.status_code == 403

    async def test_qr_invalid_token(self, client: AsyncClient):
        """QR con token inválido retorna 401."""
        response = await client.get(
            f"{API_PREFIX}/admin/qr",
            headers={"Authorization": "Bearer bad-token"},
        )
        assert response.status_code == 401


class TestQRNoRestaurant:
    """Tests cuando el usuario no tiene restaurante."""

    async def test_qr_no_restaurant(
        self, client: AsyncClient, auth_headers
    ):
        """QR sin restaurante retorna 404."""
        response = await client.get(
            f"{API_PREFIX}/admin/qr", headers=auth_headers
        )
        assert response.status_code == 404
        assert "no restaurant" in response.json()["detail"].lower()
