from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.menu import PublicMenuOut
from app.services.menu_service import MenuService

router = APIRouter(prefix="/menu", tags=["Menu"])

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
    _cache[slug] = _CacheEntry(expires_at=time.time() + MENU_CACHE_TTL_SECONDS, payload=payload)


@router.get(
    "/{slug}",
    response_model=PublicMenuOut,
    summary="Get Public Menu",
    description="""
Returns the complete public menu for a restaurant identified by its unique slug.

- Public endpoint (no authentication required).
- Uses in-memory caching to improve performance.
""",
)
async def get_public_menu(slug: str, db: AsyncSession = Depends(get_db)):
    cached = _cache_get(slug)
    if cached is not None:
        return {"source": "cache", "data": cached}

    payload = await MenuService.build_public_menu_payload(db, slug, MENU_CACHE_TTL_SECONDS)
    if not payload:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    _cache_set(slug, payload)
    return {"source": "db", "data": payload}