import json
from typing import Optional

from pos.core.models.receipt import Receipt
from pos.core.models.repositories import ReceiptRepository
from pos.infra.database import Database


class ReceiptSQLiteRepository(ReceiptRepository):
    def __init__(self, db: Database):
        self.db = db

    def create(self, receipt: Receipt) -> Receipt:
        self.db.execute(
            "INSERT INTO receipts (id, shift_id, is_open, "
            "products, gift_products, discount_price, total_price)"
            " VALUES (?,?,?,?,?,?,?)",
            (
                receipt.id,
                receipt.shift_id,
                receipt.is_open,
                json.dumps(receipt.products),
                json.dumps(receipt.gift_products),
                receipt.discount_price,
                receipt.total_price,
            ),
        )
        return receipt

    def read(self, receipt_id: str) -> Optional[Receipt]:
        row = self.db.fetchone("SELECT * FROM receipts WHERE id=?", (receipt_id,))
        if row is None:
            return None
        return Receipt(
            id=row[0],
            shift_id=row[1],
            is_open=row[2],
            products=json.loads(row[3]),
            gift_products=json.loads(row[4]),
            discount_price=row[5],
            total_price=row[6],
        )

    def update(self, receipt: Receipt) -> None:
        self.db.execute(
            "UPDATE receipts SET shift_id = ?, is_open = ?, "
            "products = ?, gift_products = ?, "
            "total_price = ?, discount_price = ? WHERE id = ?",
            (
                receipt.shift_id,
                receipt.is_open,
                json.dumps(receipt.products),
                json.dumps(receipt.gift_products),
                receipt.total_price,
                receipt.discount_price,
                receipt.id,
            ),
        )

    def delete(self, receipt_id: str) -> None:
        self.db.execute("DELETE FROM receipts WHERE id=?", (receipt_id,))
