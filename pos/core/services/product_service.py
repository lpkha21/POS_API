from typing import List, Optional

from pos.core.models.product import Product
from pos.core.models.repositories import ProductRepository


class ProductService:
    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def create_product(
        self, product_id: str, name: str, barcode: str, price: float
    ) -> Product:
        if price < 0:
            raise ValueError("Price must be non-negative.")

        # Check if a product with the same barcode already exists
        existing_product_by_barcode = self.product_repo.get_by_barcode(barcode)
        if existing_product_by_barcode:
            raise ValueError(f"Product with barcode '{barcode}' already exists.")

        # Create and add the new product
        product = Product(id=product_id, name=name, barcode=barcode, price=price)
        return self.product_repo.create(product)

    def get_product(self, product_id: str) -> Optional[Product]:
        return self.product_repo.read(product_id)

    def list_products(self) -> List[Product]:
        """Get a list of all units."""
        return self.product_repo.list()

    def update_product_price(self, product_id: str, price: int) -> None:
        if price < 0:
            raise ValueError("Price must be non-negative.")
        product = self.product_repo.read(product_id)
        if not product:
            raise ValueError("Product not found.")
        product.price = price
        self.product_repo.update(product)

    def delete_product(self, product_id: str) -> None:
        product = self.product_repo.read(product_id)
        if not product:
            raise ValueError("Product not found.")
        self.product_repo.delete(product_id)
