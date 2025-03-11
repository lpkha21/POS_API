import unittest

from pos.core.models.receipt import Receipt
from pos.infra.database import Database
from pos.infra.sqlite_repositories.receipt_sqlite_repository import (
    ReceiptSQLiteRepository,
)
from pos.infra.sqlite_repositories.sales_sqlite_repository import SalesSqliteRepository


class TestReportRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.sales_repo = SalesSqliteRepository(self.db)
        self.receipts_repo = ReceiptSQLiteRepository(self.db)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS receipts")

    def test_generate_sales_with_no_receipts(self) -> None:
        # Generate report when there are no receipts
        report = self.sales_repo.generate()
        self.assertEqual(report.n_receipts, 0)
        self.assertEqual(report.revenue, 0.0)

    def test_generate_sales_with_open_receipts(self) -> None:
        # Add an open receipt (should not be included in the report)
        receipt = Receipt(id="1", shift_id="1")
        receipt.products["1"] = 2
        receipt.total_price = 10
        self.receipts_repo.create(receipt)

        # Generate report
        report = self.sales_repo.generate()
        self.assertEqual(report.n_receipts, 0)
        self.assertEqual(report.revenue, 0.0)

    def test_generate_sales_with_closed_receipts(self) -> None:
        # Add closed receipts
        receipt = Receipt(id="1", shift_id="1")
        receipt.products["1"] = 2
        receipt.total_price = 10
        receipt.close()
        self.receipts_repo.create(receipt)
        receipt = Receipt(id="2", shift_id="1")
        receipt.products["1"] = 3
        receipt.total_price = 15
        receipt.close()
        self.receipts_repo.create(receipt)

        # Generate report
        report = self.sales_repo.generate()
        self.assertEqual(report.n_receipts, 2)
        self.assertEqual(report.revenue, 25)

    def test_generate_sales_with_mixed_receipts(self) -> None:
        # Add both open and closed receipts
        receipt = Receipt(id="1", shift_id="1")
        receipt.products["1"] = 2
        receipt.total_price = 10
        self.receipts_repo.create(receipt)
        receipt = Receipt(id="2", shift_id="1")
        receipt.products["1"] = 3
        receipt.total_price = 15
        receipt.close()
        self.receipts_repo.create(receipt)

        # Generate report
        report = self.sales_repo.generate()
        self.assertEqual(report.n_receipts, 1)  # Only closed receipts are counted
        self.assertEqual(report.revenue, 15)  # Only closed receipts are included
