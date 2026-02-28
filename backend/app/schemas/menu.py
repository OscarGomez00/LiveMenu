from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field

class PublicDishOut(BaseModel):
    id: str
    name: str
    price: float

class PublicCategoryOut(BaseModel):
    id: str
    name: str
    dishes: List[PublicDishOut] = Field(default_factory=list)

class PublicRestaurantOut(BaseModel):
    id: str
    name: str
    slug: str

class MenuCacheOut(BaseModel):
    ttl_seconds: int

class PublicMenuDataOut(BaseModel):
    restaurant: PublicRestaurantOut
    categories: List[PublicCategoryOut]
    cache: MenuCacheOut

class PublicMenuOut(BaseModel):
    source: Literal["db", "cache"]
    data: PublicMenuDataOut