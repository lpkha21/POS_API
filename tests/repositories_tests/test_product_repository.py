import unittest

from pos.core.models.product import Product
from pos.infra.database import Database
from pos.infra.sqlite_repositories.product_sqlite_repository import (
    ProductSQLiteRepository,
)


class TestProductRepository(unittest.TestCase):
    def setUp(self) -> None:
        self.db = Database()
        self.repo = ProductSQLiteRepository(self.db)

    def tearDown(self) -> None:
        self.db.execute("DROP TABLE IF EXISTS products")

    def test_create_product(self) -> None:
        product = Product(id="1", name="Apple", barcode="1234567890", price=5)
        created_product = self.repo.create(product)
        self.assertIsNotNone(product)
        if created_product is not None:
            self.assertEqual(created_product.id, "1")
            self.assertEqual(created_product.name, "Apple")
            self.assertEqual(created_product.barcode, "1234567890")
            self.assertEqual(created_product.price, 5)

    def test_read_product(self) -> None:
        product = Product(id="1", name="Apple", barcode="1234567890", price=5)
        self.repo.create(product)
        retrieved_product = self.repo.read("1")
        self.assertIsNotNone(retrieved_product)
        if retrieved_product is not None:
            self.assertEqual(retrieved_product.name, "Apple")
            self.assertEqual(retrieved_product.barcode, "1234567890")
            self.assertEqual(retrieved_product.price, 5)

    def test_update_product(self) -> None:
        product = Product(id="1", name="Apple", barcode="1234567890", price=5)
        self.repo.create(product)
        product.price = 6.0
        self.repo.update(product)
        updated_product = self.repo.read("1")
        if updated_product is not None:
            self.assertEqual(updated_product.price, 6.0)

    def test_delete_product(self) -> None:
        product = Product(id="1", name="Apple", barcode="1234567890", price=5)
        self.repo.create(product)
        self.repo.delete("1")
        deleted_product = self.repo.read("1")
        self.assertIsNone(deleted_product)

    def test_get_by_name(self) -> None:
        product = Product(id="1", name="Apple", barcode="1234567890", price=5)
        self.repo.create(product)

        # Test getting an existing product by name
        product_by_name = self.repo.get_by_name("Apple")
        self.assertIsNotNone(product_by_name)
        if product_by_name is not None:
            self.assertEqual(product_by_name.id, "1")
            self.assertEqual(product_by_name.barcode, "1234567890")
            self.assertEqual(product_by_name.price, 5)

        # Test getting a non-existent product by name
        product_by_name = self.repo.get_by_name("Banana")
        self.assertIsNone(product_by_name)

    def test_get_by_barcode(self) -> None:
        product = Product(id="1", name="Apple", barcode="1234567890", price=5)
        self.repo.create(product)

        # Test getting an existing product by barcode
        product_by_barcode = self.repo.get_by_barcode("1234567890")
        self.assertIsNotNone(product_by_barcode)
        if product_by_barcode is not None:
            self.assertEqual(product_by_barcode.id, "1")
            self.assertEqual(product_by_barcode.name, "Apple")
            self.assertEqual(product_by_barcode.price, 5)

        # Test getting a non-existent product by barcode
        product_by_barcode = self.repo.get_by_barcode("0987654321")
        self.assertIsNone(product_by_barcode)

    def test_list(self) -> None:
        product = Product(id="1", name="Apple", barcode="1234567890", price=5)
        self.repo.create(product)
        product = Product(id="2", name="Banana", barcode="0987654321", price=7)
        self.repo.create(product)

        product_list = self.repo.list()
        self.assertIsNotNone(product_list)
        self.assertEqual(len(product_list), 2)
        self.assertEqual(product_list[0].name, "Apple")
        self.assertEqual(product_list[0].barcode, "1234567890")
        self.assertEqual(product_list[0].price, 5)
        self.assertEqual(product_list[1].name, "Banana")
        self.assertEqual(product_list[1].barcode, "0987654321")
        self.assertEqual(product_list[1].price, 7)
