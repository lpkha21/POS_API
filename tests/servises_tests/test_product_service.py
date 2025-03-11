import unittest

from pos.core.services.product_service import ProductService
from pos.infra.database import Database
from pos.infra.sqlite_repositories.product_sqlite_repository import (
    ProductSQLiteRepository,
)


class TestProductService(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.product_repo = ProductSQLiteRepository(self.db)
        self.product_service = ProductService(self.product_repo)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS products")

    def test_create_product(self) -> None:
        # Test creating a new product
        product = self.product_service.create_product(
            product_id="1", name="Apple", barcode="1234567890", price=5.0
        )
        self.assertEqual(product.id, "1")
        self.assertEqual(product.name, "Apple")
        self.assertEqual(product.barcode, "1234567890")
        self.assertEqual(product.price, 5.0)

        # Test creating a product with a duplicate barcode
        with self.assertRaises(ValueError):
            self.product_service.create_product(
                product_id="2", name="Banana", barcode="1234567890", price=3.0
            )

    def test_get_product(self) -> None:
        # Create a product
        self.product_service.create_product(
            product_id="1", name="Apple", barcode="1234567890", price=5.0
        )

        # Test getting an existing product
        product = self.product_service.get_product("1")
        self.assertIsNotNone(product)
        if product is not None:
            self.assertEqual(product.name, "Apple")
            self.assertEqual(product.barcode, "1234567890")
            self.assertEqual(product.price, 5.0)

        # Test getting a non-existent product
        product = self.product_service.get_product("2")
        self.assertIsNone(product)

    def test_update_product_price(self) -> None:
        # Create a product
        self.product_service.create_product(
            product_id="1", name="Apple", barcode="1234567890", price=5.0
        )

        # Test updating the product price
        self.product_service.update_product_price("1", 6)
        product = self.product_service.get_product("1")
        if product is not None:
            self.assertEqual(product.price, 6.0)

        # Test updating the price of a non-existent product
        with self.assertRaises(ValueError):
            self.product_service.update_product_price("2", 6)

    def test_delete_product(self) -> None:
        # Create a product
        self.product_service.create_product(
            product_id="1", name="Apple", barcode="1234567890", price=5.0
        )

        # Test deleting an existing product
        self.product_service.delete_product("1")
        self.assertIsNone(self.product_service.get_product("1"))
