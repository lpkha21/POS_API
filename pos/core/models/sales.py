from pydantic import BaseModel


class Sales(BaseModel):
    n_receipts: int
    revenue: float
