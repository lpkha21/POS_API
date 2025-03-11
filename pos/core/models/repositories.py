from typing import Any, List, Optional, Protocol

from pos.core.models.campaigns import BuyNGetN, Combo, DiscountItem, DiscountPrice
from pos.core.models.product import Product
from pos.core.models.receipt import Receipt
from pos.core.models.report import Report
from pos.core.models.sales import Sales
from pos.core.models.shift import Shift


class CampaignRepository(Protocol):
    def create_discount_item(self, campaign: DiscountItem) -> DiscountItem:
        pass

    def create_discount_price(self, campaign: DiscountPrice) -> DiscountPrice:
        pass

    def create_buy_n_get_n(self, campaign: BuyNGetN) -> BuyNGetN:
        pass

    def create_combo(self, campaign: Combo) -> Combo:
        pass

    def list(self) -> List[Any]:
        pass

    def delete(self, campaign_id: str) -> None:
        pass

    def campaign_check(self, receipt: Receipt) -> None:
        pass


class ReportRepository(Protocol):
    def generate(self, shift_id: str) -> Report:
        pass


class ReceiptRepository(Protocol):
    def create(self, receipt: Receipt) -> Receipt:
        pass

    def read(self, receipt_id: str) -> Optional[Receipt]:
        pass

    def update(self, receipt: Receipt) -> None:
        pass

    def delete(self, receipt_id: str) -> None:
        pass


class ProductRepository(Protocol):
    def create(self, product: Product) -> Product:
        pass

    def read(self, product_id: str) -> Optional[Product]:
        pass

    def get_by_name(self, product_name: str) -> Optional[Product]:
        pass

    def get_by_barcode(self, product_barcode: str) -> Optional[Product]:
        pass

    def list(self) -> List[Product]:
        pass

    def update(self, product: Product) -> None:
        pass

    def delete(self, item_id: str) -> None:
        pass


class SalesRepository(Protocol):
    def generate(self) -> Sales:
        pass


class ShiftRepository(Protocol):
    def create(self, shift: Shift) -> Shift:
        pass

    def read(self, shift_id: str) -> Optional[Shift]:
        pass

    def close(self, shift_id: str) -> None:
        pass
