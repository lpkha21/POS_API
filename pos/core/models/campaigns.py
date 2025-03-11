from typing import List

from pydantic import BaseModel


class DiscountItem(BaseModel):
    id: str
    product_id: str
    discount: int


class DiscountPrice(BaseModel):
    id: str
    price: int
    discount: int


class BuyNGetN(BaseModel):
    id: str
    product_id: str
    product_amount: int
    gift_id: str
    gift_amount: int


class Combo(BaseModel):
    id: str
    products: List[str]
    discount: int
