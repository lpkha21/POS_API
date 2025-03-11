from pos.core.models.product import Product
from pos.core.models.receipt import Receipt
from pos.core.models.repositories import (
    CampaignRepository,
    ProductRepository,
    ReceiptRepository,
)


class ReceiptService:
    def __init__(
        self,
        recept_repository: ReceiptRepository,
        products_repository: ProductRepository,
        campaign_repository: CampaignRepository,
    ):
        self.receipt_repo = recept_repository
        self.products_repo = products_repository
        self.campaign_repo = campaign_repository

    def create_receipt(self, receipt_id: str, shift_id: str) -> Receipt:
        # Generate a new receipt ID using the repository
        receipt = Receipt(id=receipt_id, shift_id=shift_id)
        return self.receipt_repo.create(receipt)

    def add_product_to_receipt(
        self, receipt_id: str, product_id: str, quantity: int
    ) -> None:
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        receipt = self.receipt_repo.read(receipt_id)
        if not receipt or not receipt.is_open:
            raise ValueError("Receipt is not valid or is closed.")

        # Fetch product price from the product repository
        product = self.products_repo.read(product_id)
        if not product:
            raise ValueError("Product not found.")

        self.__add_product(receipt, product, quantity)
        self.receipt_repo.update(receipt)

    def close_receipt(self, receipt_id: str) -> None:
        receipt = self.receipt_repo.read(receipt_id)
        if not receipt or not receipt.is_open:
            raise ValueError("Receipt is not valid or is already closed.")
        receipt.close()
        self.receipt_repo.update(receipt)

    def get_receipt(self, receipt_id: str) -> Receipt:
        receipt = self.receipt_repo.read(receipt_id)
        if not receipt:
            raise ValueError("Receipt not found.")
        return receipt

    def get_receipt_total_price(self, receipt_id: str) -> float:
        """Get the total price of a receipt."""
        receipt = self.receipt_repo.read(receipt_id)
        if not receipt:
            raise ValueError("Receipt not found.")
        return receipt.discount_price

    def delete_receipt(self, receipt_id: str) -> None:
        receipt = self.receipt_repo.read(receipt_id)
        if not receipt:
            raise ValueError("Receipt not found.")
        if not receipt.is_open:
            raise ValueError("Receipt is not open")
        self.receipt_repo.delete(receipt_id)

    def __add_product(self, receipt: Receipt, product: Product, quantity: int) -> None:
        if product.id in receipt.products:
            receipt.products[product.id] += quantity
        else:
            receipt.products[product.id] = quantity

        receipt.total_price += quantity * product.price
        self.campaign_repo.campaign_check(receipt)
