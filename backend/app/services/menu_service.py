from __future__ import annotations

from typing import Any, Dict
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish


class MenuService:
    @staticmethod
    async def build_public_menu_payload(db: AsyncSession, slug: str, ttl_seconds: int) -> Dict[str, Any]:
        r = Restaurant.__table__
        c = Category.__table__
        d = Dish.__table__

        rest_stmt = select(
            r.c.id, r.c.nombre, r.c.slug, r.c.descripcion, r.c.logo_url
        ).where(r.c.slug == slug)
        rest_row = (await db.execute(rest_stmt)).first()
        if not rest_row:
            return {}

        rest_id, rest_nombre, rest_slug, rest_desc, rest_logo = rest_row

        # Solo categorías activas, ordenadas por posición
        cat_stmt = (
            select(c.c.id, c.c.nombre)
            .where(c.c.restaurant_id == rest_id, c.c.activa == True)
            .order_by(c.c.posicion.asc())
        )
        cat_rows = (await db.execute(cat_stmt)).all()
        cat_ids = [row[0] for row in cat_rows]

        dishes_by_cat: Dict[str, list[Dict[str, Any]]] = {}
        if cat_ids:
            # Solo platos disponibles y no eliminados (soft delete)
            dish_stmt = (
                select(
                    d.c.id, d.c.nombre, d.c.descripcion, d.c.precio,
                    d.c.precio_oferta, d.c.imagen_url, d.c.destacado,
                    d.c.etiquetas, d.c.category_id,
                )
                .where(
                    d.c.category_id.in_(cat_ids),
                    d.c.disponible == True,
                    d.c.eliminado_en.is_(None),
                )
                .order_by(d.c.posicion.asc().nullslast(), d.c.nombre.asc())
            )
            dish_rows = (await db.execute(dish_stmt)).all()

            for row in dish_rows:
                dish_id, dish_nombre, dish_desc, dish_precio, dish_oferta, \
                    dish_img, dish_dest, dish_tags, dish_cat_id = row
                dishes_by_cat.setdefault(str(dish_cat_id), []).append({
                    "id": str(dish_id),
                    "name": dish_nombre,
                    "description": dish_desc,
                    "price": float(dish_precio),
                    "offer_price": float(dish_oferta) if dish_oferta else None,
                    "image_url": dish_img,
                    "featured": dish_dest,
                    "tags": dish_tags,
                })

        payload: Dict[str, Any] = {
            "restaurant": {
                "id": str(rest_id),
                "name": rest_nombre,
                "slug": rest_slug,
                "description": rest_desc,
                "logo_url": rest_logo,
            },
            "categories": [
                {"id": str(cat_id), "name": cat_nombre, "dishes": dishes_by_cat.get(str(cat_id), [])}
                for cat_id, cat_nombre in cat_rows
            ],
            "cache": {"ttl_seconds": ttl_seconds},
        }
        return payload