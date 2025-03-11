import unittest

from pos.core.services.product_service import ProductService
from pos.core.services.receipt_service import ReceiptService
from pos.core.services.report_service import ReportService
from pos.core.services.shift_service import ShiftService
from pos.infra.database import Database
from pos.infra.sqlite_repositories.campaign_sqlite_repository import (
    CampaignSQLiteRepository,
)
from pos.infra.sqlite_repositories.product_sqlite_repository import (
    ProductSQLiteRepository,
)
from pos.infra.sqlite_repositories.receipt_sqlite_repository import (
    ReceiptSQLiteRepository,
)
from pos.infra.sqlite_repositories.report_sqlite_repository import (
    ReportSQLiteRepository,
)
from pos.infra.sqlite_repositories.shift_sqlite_repository import ShiftSQLiteRepository


class TestReportService(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.report_repository = ReportSQLiteRepository(self.db)
        self.shift_repository = ShiftSQLiteRepository(self.db)
        self.shift_service = ShiftService(self.shift_repository)
        self.report_service = ReportService(
            self.report_repository, self.shift_repository
        )
        self.receipt_repository = ReceiptSQLiteRepository(self.db)
        self.product_repository = ProductSQLiteRepository(self.db)
        self.campaign_repository = CampaignSQLiteRepository(self.db)
        self.receipt_service = ReceiptService(
            self.receipt_repository, self.product_repository, self.campaign_repository
        )
        self.product_service = ProductService(self.product_repository)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS shifts")
        self.db.execute("DROP TABLE IF EXISTS receipts")
        self.db.execute("DROP TABLE IF EXISTS products")
        self.db.execute("DROP TABLE IF EXISTS campaigns")

    def test_generate_report_with_receipts(self) -> None:
        self.shift_service.create_shift(shift_id="1", cashier="John")
        self.shift_service.create_shift(shift_id="2", cashier="Ann")
        self.receipt_service.create_receipt(receipt_id="1", shift_id="1")
        self.product_service.create_product(
            product_id="1", name="apple", barcode="1234567890", price=5.0
        )
        self.receipt_service.add_product_to_receipt(
            receipt_id="1", product_id="1", quantity=2
        )
        self.receipt_service.close_receipt(receipt_id="1")

        self.receipt_service.create_receipt(receipt_id="2", shift_id="1")
        self.product_service.create_product(
            product_id="2", name="Banana", barcode="0987654321", price=7.0
        )
        self.receipt_service.add_product_to_receipt(
            receipt_id="2", product_id="2", quantity=1
        )
        self.receipt_service.close_receipt(receipt_id="2")

        self.receipt_service.create_receipt(receipt_id="3", shift_id="2")
        self.receipt_service.add_product_to_receipt(
            receipt_id="3", product_id="1", quantity=1
        )
        self.receipt_service.add_product_to_receipt(
            receipt_id="3", product_id="2", quantity=1
        )
        self.receipt_service.close_receipt(receipt_id="3")

        self.receipt_service.create_receipt(receipt_id="4", shift_id="2")
        self.product_service.create_product(
            product_id="45", name="book", barcode="0987600321", price=15.0
        )
        self.receipt_service.add_product_to_receipt(
            receipt_id="4", product_id="45", quantity=1
        )

        report = self.report_service.get_x_report(shift_id="1")
        self.assertEqual(report.n_receipts, 2)
        self.assertEqual(report.revenue, 17)
        self.assertEqual(report.products, {"1": 2, "2": 1})

        shift = self.shift_service.get_shift(shift_id="1")
        self.assertEqual(shift.is_open, True)

        report = self.report_service.get_z_report(shift_id="2")
        self.assertEqual(report.n_receipts, 1)
        self.assertEqual(report.revenue, 12)
        self.assertEqual(report.products, {"1": 1, "2": 1})

        shift = self.shift_service.get_shift(shift_id="2")
        self.assertEqual(shift.is_open, False)
