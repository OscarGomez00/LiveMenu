import uuid
import pytest

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import insert

from main import app
from app.db.session import get_db

from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish

from app.db.session import Base

@pytest.fixture
async def db_session() -> AsyncSession:

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession):

    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db

    import app.api.v1.menu as menu_api

    menu_api._cache.clear()
    menu_api.MENU_CACHE_TTL_SECONDS = 60

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


async def _seed_simple_menu(db: AsyncSession, slug: str = "arepas-power"):

    r = Restaurant.__table__
    c = Category.__table__
    d = Dish.__table__

    rest_id = uuid.uuid4()
    cat_id = uuid.uuid4()
    dish_id = uuid.uuid4()

    await db.execute(
        insert(r).values(
            id=rest_id,
            nombre="Arepas Power",
            slug=slug,
            owner_id=uuid.uuid4(),
        )
    )
    await db.execute(
        insert(c).values(
            id=cat_id,
            restaurant_id=rest_id,
            nombre="Entradas",
        )
    )
    await db.execute(
        insert(d).values(
            id=dish_id,
            category_id=cat_id,
            nombre="Arepita Mini",
            precio=8000,
        )
    )
    await db.commit()

    return {"rest_id": rest_id, "cat_id": cat_id, "dish_id": dish_id}


@pytest.mark.asyncio
async def test_menu_returns_404_when_slug_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/menu/slug-que-no-existe")
    assert resp.status_code == 404
    body = resp.json()
    assert body["detail"] in ("Restaurant not found", "Not Found")


@pytest.mark.asyncio
async def test_menu_returns_structure_from_db(client: AsyncClient, db_session: AsyncSession):
    await _seed_simple_menu(db_session, slug="arepas-power")

    resp = await client.get("/api/v1/menu/arepas-power")
    assert resp.status_code == 200

    data = resp.json()
    assert data["source"] == "db"

    # Shape checks
    assert "data" in data
    assert "restaurant" in data["data"]
    assert "categories" in data["data"]
    assert "cache" in data["data"]

    restaurant = data["data"]["restaurant"]
    assert restaurant["slug"] == "arepas-power"
    assert restaurant["name"] == "Arepas Power"

    categories = data["data"]["categories"]
    assert len(categories) == 1
    assert categories[0]["name"] == "Entradas"

    dishes = categories[0]["dishes"]
    assert len(dishes) == 1
    assert dishes[0]["name"] == "Arepita Mini"
    assert dishes[0]["price"] == 8000.0


@pytest.mark.asyncio
async def test_menu_cache_second_call_returns_cache(client: AsyncClient, db_session: AsyncSession):
    await _seed_simple_menu(db_session, slug="arepas-power")

    resp1 = await client.get("/api/v1/menu/arepas-power")
    assert resp1.status_code == 200
    assert resp1.json()["source"] == "db"

    resp2 = await client.get("/api/v1/menu/arepas-power")
    assert resp2.status_code == 200
    assert resp2.json()["source"] == "cache"