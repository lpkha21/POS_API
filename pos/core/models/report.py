from typing import Dict

from pydantic import BaseModel


class Report(BaseModel):
    shift_id: str
    n_receipts: int
    products: Dict[str, int]
    revenue: float
