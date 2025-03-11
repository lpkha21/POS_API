from pos.core.models.repositories import SalesRepository
from pos.core.models.sales import Sales


class SalesService:
    def __init__(self, sales_repository: SalesRepository):
        self.sales_repo = sales_repository

    def get_sales(self) -> Sales:
        """Generate a report based on closed receipts."""
        sales = self.sales_repo.generate()
        return sales
