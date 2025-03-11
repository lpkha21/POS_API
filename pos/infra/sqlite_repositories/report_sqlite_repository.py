import json

from pos.core.models.report import Report
from pos.core.models.repositories import ReportRepository
from pos.infra.database import Database


class ReportSQLiteRepository(ReportRepository):
    def __init__(self, db: Database):
        self.db = db

    def generate(self, shift_id: str) -> Report:
        rows = self.db.fetchall(
            "SELECT products, total_price FROM receipts "
            "WHERE shift_id = ? and is_open = ?",
            (shift_id, False),
        )
        report = Report(shift_id=shift_id, n_receipts=0, products={}, revenue=0)
        if rows is None:
            return report

        report.n_receipts = len(rows)
        for row in rows:
            report.revenue += row[1]

            products = json.loads(row[0])
            for product_id, product_quantity in products.items():
                if product_id in report.products:
                    report.products[product_id] += product_quantity
                else:
                    report.products[product_id] = product_quantity

        return report
