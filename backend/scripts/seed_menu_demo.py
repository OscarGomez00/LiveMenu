from __future__ import annotations

import asyncio
import uuid
from decimal import Decimal
from datetime import datetime

from sqlalchemy import select, insert

from app.db.session import AsyncSessionLocal
from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish

try:
    from app.models.user import User
except Exception:
    from app.models import User


RESTAURANTS = [
    {
        "nombre": "Arepas Power",
        "slug": "arepas-power",
        "categories": {
            "Entradas": [("Arepita Mini", "8000.00"), ("Arepa con Queso", "12000.00")],
            "Bebidas": [("Jugo Natural", "6000.00"), ("Limonada Coco", "9000.00")],
        },
    },
    {
        "nombre": "Sushi Flex",
        "slug": "sushi-flex",
        "categories": {
            "Rolls": [("California Roll", "28000.00"), ("Dragon Roll", "35000.00")],
            "Bebidas": [("Té Verde", "7000.00"), ("Sake", "22000.00")],
        },
    },
    {
        "nombre": "Burger Brutal",
        "slug": "burger-brutal",
        "categories": {
            "Burgers": [("Clásica Brutal", "22000.00"), ("BBQ Monster", "26000.00")],
            "Sides": [("Papas Francesas", "8000.00"), ("Aros de Cebolla", "9000.00")],
        },
    },
]


def _guess_value(col_name: str):
    n = col_name.lower()
    if "email" in n:
        return f"demo_{uuid.uuid4().hex[:8]}@livemenu.local"
    if "password" in n:
        return "demo_password_hash"
    if "name" in n or "nombre" in n:
        return "Demo User"
    if "username" in n or "user" in n:
        return f"demo_{uuid.uuid4().hex[:6]}"
    if "role" in n:
        return "admin"
    if "active" in n or "enabled" in n or "is_" in n:
        return True
    if "created" in n or "updated" in n:
        return datetime.utcnow()
    return "demo"


def _build_required_kwargs(Model, preferred: dict):
    kwargs = dict(preferred)
    for col in Model.__table__.columns:
        if col.primary_key:
            continue
        if col.name in kwargs:
            continue
        has_default = col.default is not None or col.server_default is not None
        if (not col.nullable) and (not has_default):
            kwargs[col.name] = _guess_value(col.name)
    return kwargs


async def _get_or_create_owner(db) -> uuid.UUID:
    user = (await db.execute(select(User).limit(1))).scalars().first()
    if user:
        return user.id

    preferred = {}
    if "email" in User.__table__.columns:
        preferred["email"] = "demo@livemenu.local"

    user_kwargs = _build_required_kwargs(User, preferred)
    user = User(**user_kwargs)
    db.add(user)
    await db.flush()
    return user.id


async def main() -> None:
    async with AsyncSessionLocal() as db:
        owner_id = await _get_or_create_owner(db)

        for rest_data in RESTAURANTS:
            # Restaurant
            stmt = select(Restaurant).where(Restaurant.slug == rest_data["slug"])
            rest = (await db.execute(stmt)).scalars().first()

            if not rest:
                rest = Restaurant(
                    id=uuid.uuid4(),
                    nombre=rest_data["nombre"],
                    slug=rest_data["slug"],
                    owner_id=owner_id,
                )
                db.add(rest)
                await db.flush()
                print(f"Restaurant creado: {rest.slug}")
            else:
                print(f"Restaurant ya existe: {rest.slug}")

            # Categories + Dishes
            for cat_name, dishes in rest_data["categories"].items():
                cat_stmt = (
                    select(Category)
                    .where(Category.restaurant_id == rest.id)
                    .where(Category.nombre == cat_name)
                )
                category = (await db.execute(cat_stmt)).scalars().first()

                if not category:
                    category = Category(
                        id=uuid.uuid4(),
                        restaurant_id=rest.id,
                        nombre=cat_name,
                    )
                    db.add(category)
                    await db.flush()
                    print(f"Category creada: {cat_name}")

                for dish_name, price in dishes:
                    # Select ONLY existing columns (evita 'descripcion' missing column)
                    dish_exists_stmt = (
                        select(Dish.id)
                        .where(Dish.category_id == category.id)
                        .where(Dish.nombre == dish_name)
                        .limit(1)
                    )
                    dish_id = (await db.execute(dish_exists_stmt)).scalar_one_or_none()

                    if not dish_id:
                        # Insert ONLY simple columns (evita defaults ORM para columnas que no existen)
                        await db.execute(
                            insert(Dish.__table__).values(
                                id=uuid.uuid4(),
                                category_id=category.id,
                                nombre=dish_name,
                                precio=Decimal(price),
                            )
                        )
                        print(f"Dish creado: {dish_name}")

        await db.commit()
        print("\nSeed completado. Prueba estos slugs en Swagger:")
        print("- arepas-power")
        print("- sushi-flex")
        print("- burger-brutal")


if __name__ == "__main__":
    asyncio.run(main())