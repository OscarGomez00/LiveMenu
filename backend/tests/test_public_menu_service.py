import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock

from main import app
from app.api.v1 import menu as menu_module


pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def clear_cache():
    menu_module._cache.clear()


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


async def test_public_menu_404_when_slug_not_found(client, monkeypatch):
    fake = AsyncMock()
    fake.build_public_menu_payload.return_value = {}

    monkeypatch.setattr(menu_module, "MenuService", fake)

    res = await client.get("/api/v1/menu/no-existe")
    assert res.status_code == 404
    assert res.json()["detail"] == "Restaurant not found"


async def test_public_menu_200_structure(client, monkeypatch):
    slug = "arepas-power"
    payload = {
        "restaurant": {"id": "1", "name": "Arepas Power", "slug": slug},
        "categories": [],
        "generated_at": "2026-02-27T12:00:00Z",
        "cache": {"ttl_seconds": 60},
    }

    fake = AsyncMock()
    fake.build_public_menu_payload.return_value = payload
    monkeypatch.setattr(menu_module, "MenuService", fake)

    res = await client.get(f"/api/v1/menu/{slug}")
    assert res.status_code == 200

    body = res.json()
    assert body["source"] == "db"
    assert body["data"]["restaurant"]["slug"] == slug
    assert "categories" in body["data"]
    assert "generated_at" in body["data"]
    assert body["data"]["cache"]["ttl_seconds"] == 60


async def test_public_menu_cache_hit_returns_source_cache(client, monkeypatch):
    slug = "arepas-power"
    payload = {
        "restaurant": {"id": "1", "name": "Arepas Power", "slug": slug},
        "categories": [],
        "generated_at": "2026-02-27T12:00:00Z",
        "cache": {"ttl_seconds": 60},
    }

    fake = AsyncMock()
    fake.build_public_menu_payload.return_value = payload
    monkeypatch.setattr(menu_module, "MenuService", fake)

    # db test
    res1 = await client.get(f"/api/v1/menu/{slug}")
    assert res1.status_code == 200
    assert res1.json()["source"] == "db"
    assert fake.build_public_menu_payload.await_count == 1

    # cache test
    res2 = await client.get(f"/api/v1/menu/{slug}")
    assert res2.status_code == 200
    assert res2.json()["source"] == "cache"
    assert fake.build_public_menu_payload.await_count == 1  # no incrementó