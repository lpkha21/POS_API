from pos.core.models.repositories import SalesRepository
from pos.core.models.sales import Sales
from pos.infra.database import Database


class SalesSqliteRepository(SalesRepository):
    def __init__(self, db: Database):
        self.db = db

    def generate(self) -> Sales:
        rows = self.db.fetchall(
            "SELECT total_price FROM receipts WHERE is_open = ?", (False,)
        )
        sales = Sales(n_receipts=0, revenue=0)
        if not rows:
            return sales

        sales.n_receipts = len(rows)

        for row in rows:
            sales.revenue += row[0]

        return sales
