import unittest

from pos.core.models.receipt import Receipt
from pos.infra.database import Database
from pos.infra.sqlite_repositories.receipt_sqlite_repository import (
    ReceiptSQLiteRepository,
)
from pos.infra.sqlite_repositories.report_sqlite_repository import (
    ReportSQLiteRepository,
)


class TestReportRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.report_repo = ReportSQLiteRepository(self.db)
        self.receipts_repo = ReceiptSQLiteRepository(self.db)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS receipts")

    def test_generate_report_with_no_receipts(self) -> None:
        # Generate report when there are no receipts
        report = self.report_repo.generate("1")
        self.assertEqual(report.n_receipts, 0)
        self.assertEqual(report.revenue, 0.0)
        report = self.report_repo.generate("2")
        self.assertEqual(report.n_receipts, 0)
        self.assertEqual(report.revenue, 0.0)

    def test_generate_report_with_mixed_receipts(self) -> None:
        # Add both open and closed receipts
        receipt = Receipt(id="1", shift_id="1")
        receipt.products["1"] = 2
        receipt.total_price = 10
        self.receipts_repo.create(receipt)
        receipt = Receipt(id="2", shift_id="1")
        receipt.products["48"] = 3
        receipt.total_price = 12
        receipt.close()
        self.receipts_repo.create(receipt)

        receipt = Receipt(id="3", shift_id="2")
        receipt.products["765"] = 1
        receipt.products["123"] = 1
        receipt.total_price = 34
        receipt.close()
        self.receipts_repo.create(receipt)
        receipt = Receipt(id="4", shift_id="2")
        receipt.products["1"] = 3
        receipt.total_price = 15
        receipt.close()
        self.receipts_repo.create(receipt)

        # Generate report
        report = self.report_repo.generate("1")
        self.assertEqual(report.n_receipts, 1)  # Only closed receipts are counted
        self.assertEqual(report.products, {"48": 3})
        self.assertEqual(report.revenue, 12)  # Only closed receipts are included

        report = self.report_repo.generate("2")
        self.assertEqual(report.n_receipts, 2)
        self.assertEqual(report.products, {"765": 1, "123": 1, "1": 3})
        self.assertEqual(report.revenue, 49)
