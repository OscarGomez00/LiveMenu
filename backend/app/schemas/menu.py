from __future__ import annotations

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class PublicDishOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    offer_price: Optional[float] = None
    image_url: Optional[str] = None
    available: bool = True
    featured: bool = False
    tags: List[str] = Field(default_factory=list)


class PublicCategoryOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    position: Optional[int] = None
    dishes: List[PublicDishOut] = Field(default_factory=list)


class PublicRestaurantOut(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    hours: Optional[dict] = None


class MenuCacheOut(BaseModel):
    ttl_seconds: int


class PublicMenuDataOut(BaseModel):
    restaurant: PublicRestaurantOut
    categories: List[PublicCategoryOut]
    generated_at: str
    cache: MenuCacheOut


class PublicMenuOut(BaseModel):
    source: Literal["db", "cache"]
    data: PublicMenuDataOut