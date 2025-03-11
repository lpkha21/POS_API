from typing import List, Optional

from pos.core.models.product import Product
from pos.core.models.repositories import ProductRepository
from pos.infra.database import Database


class ProductSQLiteRepository(ProductRepository):
    def __init__(self, db: Database):
        self.db = db

    def create(self, product: Product) -> Product:
        self.db.execute(
            "INSERT INTO products (id, name, barcode, price) VALUES (?,?,?,?)",
            (product.id, product.name, product.barcode, product.price),
        )
        return product

    def read(self, product_id: str) -> Optional[Product]:
        row = self.db.fetchone("SELECT * FROM products WHERE id = ?", (product_id,))
        if row is None:
            return None
        return Product(id=row[0], name=row[1], barcode=row[2], price=row[3])

    def update(self, product: Product) -> None:
        self.db.execute(
            "UPDATE products SET name = ?, barcode = ?, price = ? WHERE id = ?",
            (product.name, product.barcode, product.price, product.id),
        )

    def delete(self, product_id: str) -> None:
        self.db.execute("DELETE FROM products WHERE id = ?", (product_id,))

    def list(self) -> List[Product]:
        rows = self.db.fetchall("SELECT * FROM products")
        return [
            Product(id=row[0], name=row[1], barcode=row[2], price=row[3])
            for row in rows
        ]

    def get_by_barcode(self, product_barcode: str) -> Optional[Product]:
        row = self.db.fetchone(
            "SELECT * FROM products WHERE barcode = ?", (product_barcode,)
        )
        if row is None:
            return None
        return Product(id=row[0], name=row[1], barcode=row[2], price=row[3])

    def get_by_name(self, product_name: str) -> Optional[Product]:
        row = self.db.fetchone("SELECT * FROM products WHERE name = ?", (product_name,))
        if row is None:
            return None
        return Product(id=row[0], name=row[1], barcode=row[2], price=row[3])
