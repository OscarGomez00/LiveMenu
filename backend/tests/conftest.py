"""
Configuración compartida de pytest para tests de LiveMenu.
Provee fixtures de base de datos in-memory (SQLite), app de test y cliente HTTP.

Usa un patrón de conexión única: todas las sesiones (tanto directas como a través
de la app FastAPI) comparten la misma AsyncConnection, garantizando que todas
las operaciones vean las mismas tablas en la BD in-memory de SQLite.
"""
import asyncio
import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.core.security import create_access_token, get_password_hash
from app.db.session import Base, get_db

# ---------------------------------------------------------------------------
# Import ALL models so they register their tables in Base.metadata
# BEFORE create_all is called.  Without this, the first test would see
# an empty metadata and no tables would be created.
# ---------------------------------------------------------------------------
import app.models.user  # noqa: F401
import app.models.restaurant  # noqa: F401
import app.models.category  # noqa: F401
import app.models.dish  # noqa: F401

# ---------------------------------------------------------------------------
# SQLite UUID compatibility: render PostgreSQL UUID as VARCHAR(36)
# ---------------------------------------------------------------------------
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.compiler import compiles


@compiles(PG_UUID, "sqlite")
def _compile_uuid_sqlite(type_, compiler, **kw):
    return "VARCHAR(36)"


# ---------------------------------------------------------------------------
# Engine (shared in-memory SQLite via StaticPool)
# ---------------------------------------------------------------------------
engine_test = create_async_engine(
    "sqlite+aiosqlite://",
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False},
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def event_loop():
    """Crea un event loop para toda la sesión de tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def _connection():
    """
    Fixture central: mantiene UNA sola conexión abierta durante cada test.
    Crea las tablas al inicio y las destruye al final.
    Todas las demás fixtures derivan sus sesiones de esta conexión.
    """
    async with engine_test.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()
        yield conn
        await conn.run_sync(Base.metadata.drop_all)
        await conn.commit()


@pytest_asyncio.fixture
async def db_session(_connection) -> AsyncGenerator[AsyncSession, None]:
    """Provee una sesión de BD para tests directos (sin pasar por la app)."""
    session = AsyncSession(bind=_connection, expire_on_commit=False)
    try:
        yield session
    finally:
        await session.close()


@pytest_asyncio.fixture
async def app(_connection):
    """Crea la app FastAPI con la BD de test inyectada."""
    from main import app as fastapi_app

    async def override_get_db():
        session = AsyncSession(bind=_connection, expire_on_commit=False)
        try:
            yield session
        finally:
            await session.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP async para tests de endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession):
    """Crea un usuario de test en la BD."""
    from app.models.user import User

    user = User(
        id=uuid.uuid4(),
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user) -> dict:
    """Headers con token JWT válido para el usuario de test."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def test_restaurant(db_session: AsyncSession, test_user):
    """Crea un restaurante de test asociado al usuario."""
    from app.models.restaurant import Restaurant

    restaurant = Restaurant(
        id=uuid.uuid4(),
        nombre="Test Restaurant",
        slug="test-restaurant",
        owner_id=test_user.id,
    )
    db_session.add(restaurant)
    await db_session.commit()
    await db_session.refresh(restaurant)
    return restaurant
