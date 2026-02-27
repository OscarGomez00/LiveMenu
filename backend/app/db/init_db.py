"""
Script de inicialización de la base de datos.
Crea todas las tablas definidas en los modelos.
"""
import asyncio
from app.db.session import engine, Base
from app.models import User, Restaurant, Category, Dish


async def init_db():
    """Inicializa la base de datos creando todas las tablas."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    print("Base de datos inicializada correctamente")


if __name__ == "__main__":
    asyncio.run(init_db())
