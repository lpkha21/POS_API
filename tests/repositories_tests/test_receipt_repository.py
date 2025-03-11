import unittest

from pos.core.models.product import Product
from pos.core.models.receipt import Receipt
from pos.infra.database import Database
from pos.infra.sqlite_repositories.product_sqlite_repository import (
    ProductSQLiteRepository,
)
from pos.infra.sqlite_repositories.receipt_sqlite_repository import (
    ReceiptSQLiteRepository,
)


class TestReceiptRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.repo = ReceiptSQLiteRepository(self.db)
        self.product_repo = ProductSQLiteRepository(self.db)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS receipts")
        self.db.execute("DROP TABLE IF EXISTS products")

    def test_create_receipt(self) -> None:
        receipt = Receipt(id="1", shift_id="1")
        created_receipt = self.repo.create(receipt)
        self.assertIsNotNone(created_receipt)
        self.assertEqual(created_receipt.id, "1")
        self.assertEqual(created_receipt.shift_id, "1")
        self.assertTrue(created_receipt.is_open)
        self.assertEqual(created_receipt.total_price, 0)

    def test_read_receipt_with_products(self) -> None:
        # Create a product
        product = Product(id="1", name="Apple", barcode="1234567890", price=5)
        self.product_repo.create(product)

        # Create a receipt and add the product
        receipt = Receipt(id="1", shift_id="1")
        receipt.products["1"] = 2
        receipt.total_price = 10
        self.repo.create(receipt)

        # Read the receipt and verify the product price
        retrieved_receipt = self.repo.read("1")
        self.assertIsNotNone(retrieved_receipt)
        if retrieved_receipt is not None:
            self.assertEqual(retrieved_receipt.id, "1")
            self.assertEqual(retrieved_receipt.products, {"1": 2})
            self.assertEqual(retrieved_receipt.total_price, 10)

    def test_update_receipt(self) -> None:
        # Create a product
        product1 = Product(id="1", name="Apple", barcode="1234567890", price=5)
        self.product_repo.create(product1)

        # Create a receipt and add the product
        receipt = Receipt(id="1", shift_id="1")
        receipt.products["1"] = 2
        receipt.total_price = 10
        self.repo.create(receipt)

        # Update the receipt with another product
        product2 = Product(id="2", name="Banana", barcode="0987654321", price=7)
        self.product_repo.create(product2)
        receipt.products["2"] = 3
        receipt.total_price = 31
        self.repo.update(receipt)

        # Read the updated receipt and verify the total price
        updated_receipt = self.repo.read("1")
        self.assertIsNotNone(updated_receipt)
        if updated_receipt is not None:
            self.assertEqual(updated_receipt.total_price, 31)
            self.assertEqual(updated_receipt.products, {"1": 2, "2": 3})

    def test_delete_receipt(self) -> None:
        receipt = Receipt(id="1", shift_id="1")
        self.repo.create(receipt)
        self.repo.delete("1")
        deleted_receipt = self.repo.read("1")
        self.assertIsNone(deleted_receipt)
