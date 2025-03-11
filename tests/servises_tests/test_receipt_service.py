import unittest

from pos.core.services.product_service import ProductService
from pos.core.services.receipt_service import ReceiptService
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


class TestReceiptService(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.receipt_repository = ReceiptSQLiteRepository(self.db)
        self.product_repository = ProductSQLiteRepository(self.db)
        self.campaign_repository = CampaignSQLiteRepository(self.db)
        self.receipt_service = ReceiptService(
            self.receipt_repository, self.product_repository, self.campaign_repository
        )
        self.product_service = ProductService(self.product_repository)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS products")
        self.db.execute("DROP TABLE IF EXISTS receipts")
        self.db.execute("DROP TABLE IF EXISTS campaigns")

    def test_create_receipt(self) -> None:
        # Test opening a new receipt
        receipt = self.receipt_service.create_receipt(receipt_id="1", shift_id="1")
        self.assertEqual(receipt.id, "1")
        self.assertEqual(receipt.shift_id, "1")
        self.assertTrue(receipt.is_open)
        self.assertEqual(receipt.total_price, 0)

    def test_get_receipt(self) -> None:
        self.receipt_service.create_receipt(receipt_id="1", shift_id="1")
        receipt = self.receipt_service.get_receipt(receipt_id="1")
        self.assertEqual(receipt.id, "1")
        self.assertEqual(receipt.shift_id, "1")
        self.assertTrue(receipt.is_open)
        self.assertEqual(receipt.total_price, 0)

    def test_add_product_to_receipt(self) -> None:
        # Open a receipt
        self.receipt_service.create_receipt(receipt_id="1", shift_id="1")

        # Create a product
        self.product_service.create_product(
            product_id="1", name="Apple", barcode="1234567890", price=5.0
        )

        # Test adding a product to the receipt
        self.receipt_service.add_product_to_receipt(
            receipt_id="1", product_id="1", quantity=2
        )
        receipt = self.receipt_service.get_receipt(receipt_id="1")
        self.assertIsNotNone(receipt)
        self.assertEqual(receipt.id, "1")
        self.assertEqual(receipt.shift_id, "1")
        self.assertEqual(receipt.is_open, 1)
        self.assertEqual(len(receipt.products), 1)
        self.assertEqual(receipt.total_price, 10.0)

        # Test adding a product to a non-existent receipt
        with self.assertRaises(ValueError):
            self.receipt_service.add_product_to_receipt(
                receipt_id="2", product_id="1", quantity=2
            )

        # Test adding a non-existent product to the receipt
        with self.assertRaises(ValueError):
            self.receipt_service.add_product_to_receipt(
                receipt_id="1", product_id="2", quantity=2
            )

    def test_close_receipt(self) -> None:
        # Open a receipt
        self.receipt_service.create_receipt(receipt_id="1", shift_id="1")

        # Test closing the receipt
        self.receipt_service.close_receipt(receipt_id="1")
        receipt = self.receipt_service.get_receipt(receipt_id="1")
        self.assertFalse(receipt.is_open)

        # Test closing a non-existent receipt
        with self.assertRaises(ValueError):
            self.receipt_service.close_receipt(receipt_id="2")

    def test_delete_receipt(self) -> None:
        # Open a receipt
        self.receipt_service.create_receipt(receipt_id="1", shift_id="1")

        # Test deleting the receipt
        self.receipt_service.delete_receipt(receipt_id="1")
        with self.assertRaises(ValueError):
            self.receipt_service.get_receipt(receipt_id="1")

        # Test deleting a non-existent receipt
        with self.assertRaises(ValueError):
            self.receipt_service.delete_receipt(receipt_id="2")
