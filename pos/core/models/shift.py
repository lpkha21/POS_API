from pydantic import BaseModel


class Shift(BaseModel):
    id: str
    cashier: str
    is_open: bool = True
