from typing import Dict

from pydantic import BaseModel


class Receipt(BaseModel):
    id: str
    shift_id: str
    is_open: bool = True
    products: Dict[str, int] = {}  # Maps product_id to quantity
    gift_products: Dict[str, int] = {}
    discount_price: float = 0
    total_price: float = 0

    def close(self) -> None:
        self.is_open = False
