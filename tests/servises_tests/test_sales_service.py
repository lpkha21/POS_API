import unittest

from pos.core.services.product_service import ProductService
from pos.core.services.receipt_service import ReceiptService
from pos.core.services.sales_service import SalesService
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
from pos.infra.sqlite_repositories.sales_sqlite_repository import SalesSqliteRepository


class TestSalesService(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.sales_repo = SalesSqliteRepository(self.db)
        self.sales_service = SalesService(self.sales_repo)
        self.receipt_repository = ReceiptSQLiteRepository(self.db)
        self.product_repository = ProductSQLiteRepository(self.db)
        self.campaign_repository = CampaignSQLiteRepository(self.db)
        self.receipt_service = ReceiptService(
            self.receipt_repository, self.product_repository, self.campaign_repository
        )
        self.product_service = ProductService(self.product_repository)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS receipts")
        self.db.execute("DROP TABLE IF EXISTS products")
        self.db.execute("DROP TABLE IF EXISTS campaigns")

    def test_generate_report_with_no_receipts(self) -> None:
        # Test generating a report when there are no receipts
        sales = self.sales_service.get_sales()
        self.assertEqual(sales.n_receipts, 0)
        self.assertEqual(sales.revenue, 0)

    def test_generate_sales_with_receipts(self) -> None:
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

        sales = self.sales_service.get_sales()
        self.assertEqual(sales.n_receipts, 2)
        self.assertEqual(sales.revenue, 17)
