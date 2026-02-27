from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.restaurant import Restaurant
from app.models.category import Category
from app.models.dish import Dish
from app.db.session import get_db
from app.schemas.menu import PublicMenuOut

from app.services.menu_service import MenuService

router = APIRouter(prefix="/menu", tags=["Menu"])

# TTL
MENU_CACHE_TTL_SECONDS = int(os.getenv("MENU_CACHE_TTL_SECONDS", "60"))

@dataclass(frozen=True)
class _CacheEntry:
    expires_at: float
    payload: Dict[str, Any]

_cache: Dict[str, _CacheEntry] = {}

def _cache_get(slug: str) -> Optional[Dict[str, Any]]:
    entry = _cache.get(slug)
    if not entry:
        return None

    if time.time() >= entry.expires_at:
        _cache.pop(slug, None)
        return None

    return entry.payload

def _cache_set(slug: str, payload: Dict[str, Any]) -> None:
    _cache[slug] = _CacheEntry(
        expires_at=time.time() + MENU_CACHE_TTL_SECONDS, 
        payload=payload
        )


#QueryHelpers
async def _get_restaurant_by_slug(db: AsyncSession, slug: str) -> Optional[Restaurant]:
    restau = select(Restaurant).where(Restaurant.slug == slug)
    return (await db.execute(restau)).scalars().all()

async def _get_category_by_restaurant(db: AsyncSession, restaurant_id: UUID) -> list[Category]:
    cate = select(Category).where(Category.restaurant_id == restaurant_id)
    return (await db.execute(cate)).scalars().all()

async def _get_dishes_by_category_ids(db: AsyncSession, category_ids: list[UUID]) -> list[Dish]:
    if not category_ids:
        return []
    dishi = select(Dish).where(Dish.category_id.in_(category_ids))
    return (await db.execute(dishi)).scalars().all()

#PublicEndPoint CU-06

@router.get(
        "/{slug}", 
        response_model=PublicMenuOut,
        summary="Get Public Menu",
        description="""
        Returns the complete public menu for a restaurant identified by its unique slug.\n
            - Public endpoint (no authentication required).\n
            - Uses in-memory caching to improve performance.\n
            - Includes restaurant metadata, categories, and dishes.\n
        """,
    )
async def get_public_menu(slug: str, db: AsyncSession = Depends(get_db)):

    cach = _cache_get(slug)
    if cach is not None:
        return {"source": "cache", "data": cach}

    payload = await MenuService.build_public_menu_payload(db, slug, MENU_CACHE_TTL_SECONDS)
    if not payload:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    _cache_set(slug, payload)

    return {"source": "db", "data": payload}