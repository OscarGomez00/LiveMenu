from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class PublicDishOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    price: float
    offer_price: Optional[float] = None
    image_url: Optional[str] = None
    featured: Optional[bool] = False
    tags: Optional[list] = None


class PublicCategoryOut(BaseModel):
    id: str
    name: str
    dishes: List[PublicDishOut] = Field(default_factory=list)


class PublicRestaurantOut(BaseModel):
    id: str
    name: str
    slug: str
    description: Optional[str] = None
    logo_url: Optional[str] = None


class MenuCacheOut(BaseModel):
    ttl_seconds: int


class PublicMenuDataOut(BaseModel):
    restaurant: PublicRestaurantOut
    categories: List[PublicCategoryOut]
    cache: MenuCacheOut


class PublicMenuOut(BaseModel):
    source: Literal["db", "cache"]
    data: PublicMenuDataOut