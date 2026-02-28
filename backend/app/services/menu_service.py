from __future__ import annotations

from typing import Any, Dict, List
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish


class MenuService:
    @staticmethod
    async def build_public_menu_payload(db: AsyncSession, slug: str, ttl_seconds: int,) -> Dict[str, Any]:
        rest_re = select(Restaurant).where(Restaurant.slug == slug)
        restau = (await db.execute(rest_re)).scalars().first()
        if not restau:
            return {}

        cat_cat = select(Category).where(Category.restaurant_id == restau.id)
        categories = (await db.execute(cat_cat)).scalars().all()

        cat_ids = [cat.id for cat in categories]

        if cat_ids:
            dish_dih = select(Dish).where(Dish.category_id.in_(cat_ids))
            dishes = (await db.execute(dish_dih)).scalars().all()
        else:
            dishes = []

        dishes_by_cat: Dict[str, list[Dict[str, Any]]] = {}
        for dis in dishes:
            dishes_by_cat.setdefault(str(dis.category_id), []).append(
                {
                    "id": str(dis.id),
                    "name": dis.nombre,
                    "description": getattr(dis, "descripcion", None),
                    "price": float(dis.precio),
                    "offer_price": float(getattr(dis, "precio_oferta", None)) if getattr(dis, "precio_oferta", None) else None,
                    "image_url": getattr(dis, "imagen_url", None),
                    "available": getattr(dis, "disponible", True),
                    "featured": getattr(dis, "destacado", False),
                    "tags": getattr(dis, "etiquetas", None) or [],
                }
            )

        payload = {
            "restaurant": {
                "id": str(restau.id),
                "name": restau.nombre,
                "slug": restau.slug,
                "description": getattr(restau, "descripcion", None),
                "logo_url": getattr(restau, "logo_url", None),
                "phone": getattr(restau, "telefono", None),
                "address": getattr(restau, "direccion", None),
                "hours": getattr(restau, "horarios", None),
            },
            "categories": [
                {
                    "id": str(cat.id),
                    "name": cat.nombre,
                    "description": getattr(cat, "descripcion", None),
                    "position": getattr(cat, "posicion", None),
                    "dishes": dishes_by_cat.get(str(cat.id), []),
                }
                for cat in categories
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "cache": {"ttl_seconds": ttl_seconds},
        }

        return payload