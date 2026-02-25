import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from uuid import uuid4

from app.db.session import Base
from app.core.config import settings
from app.models.category import Category
from app.models.restaurant import Restaurant

# Usar base de datos de prueba (SQLite en memoria o BD de test)
# Para simplificar MVP, usaremos una base de datos de prueba en Postgres si está disponible,
# o podemos usar SQLite para unit tests.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session")
def event_loop():
    """Crear un loop de eventos para la sesión de pruebas."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Inicializar base de datos de prueba."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fixture para obtener una sesión de BD limpia por cada test."""
    async with AsyncSessionLocal() as session:
        yield session
        # Limpiar datos después de cada test para aislamiento
        for table in reversed(Base.metadata.sorted_tables):
            await session.execute(table.delete())
        await session.commit()

from app.models.user import User

@pytest.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """Fixture para crear un usuario de prueba."""
    user = User(
        id=uuid4(),
        email=f"test_{uuid4().hex[:6]}@example.com",
        hashed_password="password"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def sample_restaurant(db_session: AsyncSession, sample_user: User) -> Restaurant:
    """Fixture para crear un restaurante de prueba."""
    restaurant = Restaurant(
        id=uuid4(),
        nombre="Restaurante de Prueba",
        slug=f"test-restaurant-{uuid4().hex[:6]}",
        owner_id=sample_user.id
    )
    db_session.add(restaurant)
    await db_session.commit()
    await db_session.refresh(restaurant)
    return restaurant

@pytest.fixture
async def sample_category(db_session: AsyncSession, sample_restaurant: Restaurant) -> Category:
    """Fixture para crear una categoría de prueba."""
    category = Category(
        id=uuid4(),
        nombre="Categoría de Prueba",
        restaurant_id=sample_restaurant.id
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category

